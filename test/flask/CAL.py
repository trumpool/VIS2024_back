# -*- coding: utf-8 -*-
"""
Created on Wed Apr 26 15:32:03 2023

@author: weist
"""

import open3d as o3d
import numpy as np
import copy
import time
import os
import sys


def draw_registration_result(source, target, transform):
    # ply1.paint_uniform_color([1, 0.706, 0])
    # ply2.paint_uniform_color([0, 0.651, 0.929])
    source_view = copy.deepcopy(source)
    target_view = copy.deepcopy(target)
    source_view.transform(transform)
    # translation_vector = np.array([2.5, 0, 0])
    # target_view.points = o3d.utility.Vector3dVector(np.asarray(target_view.points) + translation_vector)
    #
    # translation_vector = np.array([-2.5, 0, 0])
    # source_view.points = o3d.utility.Vector3dVector(np.asarray(source_view.points) + translation_vector)
    o3d.visualization.draw_geometries([source_view, target_view])


def save_pcd(source, target, transform):
    Combined_pcd = source.transform(transform) + target
    o3d.io.write_point_cloud('Mapped_PCD.ply', Combined_pcd)


def preprocess_point_cloud(pcd, voxel_size):
    print(":: Downsample with a voxel size {:.3f}".format(voxel_size))
    pcd_down = pcd.voxel_down_sample(voxel_size)

    radius_normal = voxel_size * 2
    print(":: Estimate normal with search radius {:.3f}".format(radius_normal))
    pcd_down.estimate_normals(
        o3d.geometry.KDTreeSearchParamHybrid(radius=radius_normal, max_nn=30))

    radius_feature = voxel_size * 5
    print(":: Compute FPFH feature with search radius {:.3f}".format(radius_feature))
    pcd_fpfh = o3d.pipelines.registration.compute_fpfh_feature(
        pcd_down,
        o3d.geometry.KDTreeSearchParamHybrid(radius_feature, max_nn=100))
    return pcd_down, pcd_fpfh


def execute_global_registration(source_down, target_down, source_fpfh, target_fpfh, voxel_size):
    distance_threshold = voxel_size * 1.5
    # distance_threshold = voxel_size * 0.8
    print(":: RANSAC registration on downsampled point clouds.")
    print("   Since the downsampling voxel size is {:.3f}".format(voxel_size))
    print("   we use a liberal distance threshold {:.3f}".format(distance_threshold))
    result = o3d.pipelines.registration.registration_ransac_based_on_feature_matching(
        source_down, target_down, source_fpfh, target_fpfh, True, distance_threshold,
        o3d.pipelines.registration.TransformationEstimationPointToPoint(False),
        3, [
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnEdgeLength(0.9),
            o3d.pipelines.registration.CorrespondenceCheckerBasedOnDistance(distance_threshold)],
        o3d.pipelines.registration.RANSACConvergenceCriteria(100000, 0.999))
    return result


def refine_registration(source, target, result_ransac, voxel_size):
    distance_threshold = voxel_size * 0.4
    print(":: Point-to-plane ICP registration is applied on orginal point")
    print("   cloud to refine the alignment. This time we use a stirct")
    print("   distance threshold {:.3f}".format(distance_threshold))
    source.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
    target.estimate_normals(search_param=o3d.geometry.KDTreeSearchParamHybrid(radius=0.1, max_nn=30))
    result = o3d.pipelines.registration.registration_icp(
        source, target, distance_threshold, result_ransac.transformation,
        o3d.pipelines.registration.TransformationEstimationPointToPlane())
    return result


def execute_fast_global_registration(source_down, target_down, source_fpfh, target_fpfh, voxel_size):
    distance_threshold = voxel_size * 0.4
    print(":: Apply fast global registration with distance threshold {:.3f}".format(distance_threshold))
    result = o3d.pipelines.registration.registration_fgr_based_on_feature_matching(
        source_down, target_down, source_fpfh, target_fpfh,
        o3d.pipelines.registration.FastGlobalRegistrationOption(maximum_correspondence_distance=distance_threshold))
    return result


def cal_dis():
    ply1 = o3d.io.read_point_cloud("C:\\Users\\oewt\\Desktop\\ply\\ply\\reconstruction.ply")
    ply2 = o3d.io.read_point_cloud("C:\\Users\\oewt\\Desktop\\ply\\ply\\ground_truth.ply")
    # Step 2: Radius Outlier Removal
    cl, ind = ply1.remove_radius_outlier(nb_points=16, radius=0.015)
    ply1 = ply1.select_by_index(ind)

    # Step 3: 归一化操作
    # 计算中位数中心
    median_center_recon = np.median(np.asarray(ply1.points), axis=0)
    median_center_GT = np.median(np.asarray(ply2.points), axis=0)

    # 平移到原点
    ply1.points = o3d.utility.Vector3dVector(np.asarray(ply1.points) - median_center_recon)
    ply2.points = o3d.utility.Vector3dVector(np.asarray(ply2.points) - median_center_GT)

    # 使用距离的中位数在各方向上进行缩放
    median_dist_recon = np.median(np.linalg.norm(np.asarray(ply1.points), axis=1))
    median_dist_GT = np.median(np.linalg.norm(np.asarray(ply2.points), axis=1))

    ply1.points = o3d.utility.Vector3dVector(np.asarray(ply1.points) / median_dist_recon)
    ply2.points = o3d.utility.Vector3dVector(np.asarray(ply2.points) / median_dist_GT)

    # Step 4: 预处理点云（降采样，法线估计，FPFH特征计算）。
    trans_init = np.asarray([[0.0, 0.0, 1.0, 0.0], [1.0, 0.0, 0.0, 0.0],
                             [0.0, 1.0, 0.0, 0.0], [0.0, 0.0, 0.0, 1.0]])
    ply1.transform(trans_init)
    # draw_registration_result(ply1, ply2, np.identity(4))

    voxel_size = 0.01
    source_down, source_fpfh = preprocess_point_cloud(ply1, voxel_size)
    target_down, target_fpfh = preprocess_point_cloud(ply2, voxel_size)

    start = time.time()
    # 使用RANSAC执行全局配准。
    result_ransac = execute_global_registration(source_down, target_down, source_fpfh, target_fpfh, voxel_size)
    print("Global registration took {:.3f} sec.\n".format(time.time() - start))
    print(result_ransac)
    print("Result transform: {}".format(result_ransac.transformation))
    # draw_registration_result(source_down, target_down, result_ransac.transformation)
    # draw_registration_result(ply1, ply2, result_ransac.transformation)
    # 使用ICP细化配准。
    result_icp = refine_registration(ply1, ply2, result_ransac, voxel_size)
    print(result_icp)
    # draw_registration_result(ply1, ply2, result_icp.transformation)

    # save_pcd(ply1, ply2, result_icp.transformation)

    # The result of fast registration is not good.
    start = time.time()
    # 执行快速全局配准并使用ICP细化结果
    result_fast = execute_fast_global_registration(source_down, target_down, source_fpfh, target_fpfh, voxel_size)
    print("fast global registration took {:.3f} sec.\n".format(time.time() - start))
    print(result_fast)
    # draw_registration_result(source_down, target_down, result_fast.transformation)
    # draw_registration_result(ply1, ply2, result_fast.transformation)
    result_icp = refine_registration(ply1, ply2, result_fast, voxel_size)
    print(result_icp)
    # draw_registration_result(ply1, ply2, result_icp.transformation)
    # Step 5: 计算 Hausdorff Distance
    distances = ply2.compute_point_cloud_distance(ply1)

    # Step 6: 根据 Hausdorff Distance 重新赋予每个点颜色
    distances = np.asarray(distances)
    distances = np.clip(distances, 0, 0.5)
    colors = plt.get_cmap("coolwarm")(distances / np.max(distances))[:, :3]
    ply2.colors = o3d.utility.Vector3dVector(colors)
    return ply1, ply2


