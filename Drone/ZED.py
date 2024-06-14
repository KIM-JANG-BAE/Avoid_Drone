#!/usr/bin/env python3

import sys
import time
import pyzed.sl as sl
import argparse
import asyncio
import websockets
import pickle
import numpy as np
import cv2
import subprocess

'''
def convert_mesh_to_image(mesh):
    # Get the vertices and triangles from the mesh
   
    vertices = mesh.vertices
    triangles = mesh.triangles.astype(int)
   
    # Convert vertices to numpy array
    #vertices = np.array(vertices, dtype=np.float32)
    #triangles = np.array(triangles, dtype=np.int32)
   
    if len(vertices) == 0 or len(triangles) == 0:
        return 0
   
    projection_matrix = vertices[:, :2]

    # 3D 메쉬 데이터를 2D로 투영
    #projected_vertices = np.dot(vertices, projection_matrix.T)
   
    # Create a blank image
    image = np.zeros((1080, 1920, 3), dtype=np.uint8)

    # Draw the mesh on the image
    for triangle in triangles:
        pts = projection_matrix[triangle].astype(int)
        pts = pts[:, :2]
        cv2.polylines(image, [pts], isClosed=True, color=(255, 255, 255), thickness=1)
   
    #cv2.imshow("mesh", image)
   
    return image
'''  
   
   
async def main_async():
    i = 0
    build_mesh = True
    init = sl.InitParameters()
    init.depth_mode = sl.DEPTH_MODE.QUALITY
    init.coordinate_units = sl.UNIT.METER
    init.coordinate_system = sl.COORDINATE_SYSTEM.RIGHT_HANDED_Y_UP  # OpenGL's coordinate system is right-handed    
    init.depth_maximum_distance = 8.0
    init.camera_resolution = sl.RESOLUTION.HD720
   
   
    zed = sl.Camera()
   
   
   
    while True:
        status = zed.open(init)
        if status == sl.ERROR_CODE.SUCCESS:
            break
        else:
            zed.close()
   
    #status = zed.open(init)
   
   
   
   
    camera_infos = zed.get_camera_information()
    pose = sl.Pose()
   
    tracking_state = sl.POSITIONAL_TRACKING_STATE.OFF
    positional_tracking_parameters = sl.PositionalTrackingParameters()
    positional_tracking_parameters.set_floor_as_origin = False
    returned_state = zed.enable_positional_tracking(positional_tracking_parameters)

    spatial_mapping_parameters = sl.SpatialMappingParameters(resolution=sl.MAPPING_RESOLUTION.LOW,
                                                                 mapping_range=sl.MAPPING_RANGE.LONG,
                                                                 max_memory_usage=2048, save_texture=True,
                                                                 use_chunk_only=True, reverse_vertex_order=False,
                                                                 map_type=sl.SPATIAL_MAP_TYPE.MESH)
    pymesh = sl.Mesh()
   
    tracking_state = sl.POSITIONAL_TRACKING_STATE.OFF
    mapping_state = sl.SPATIAL_MAPPING_STATE.NOT_ENABLED

    zed.enable_spatial_mapping(spatial_mapping_parameters)
   
    runtime_parameters = sl.RuntimeParameters()
    runtime_parameters.confidence_threshold = 50
   
    mapping_activated = True
   
    image = sl.Mat()
                   
    pose = sl.Pose()

    last_call = time.time()
    save_count = 0	
   
    while True:
        server_address = '203.255.57.136'
        server_port = 5258
       
       
       
        try:
            async with websockets.connect(f"ws://{server_address}:{server_port}") as websocket:
           
                await websocket.send("streamer")
           
                while True:
                    if zed.grab(runtime_parameters) == sl.ERROR_CODE.SUCCESS:
                        zed.retrieve_image(image, sl.VIEW.LEFT)
                       
                        image2 = image.get_data()

                        tracking_state = zed.get_position(pose)

                        if mapping_activated:
                            mapping_state = zed.get_spatial_mapping_state()
                            duration = time.time() - last_call  
                            if duration > 0.5:
                                zed.request_spatial_map_async()
                                last_call = time.time()
                   
                            if zed.get_spatial_map_request_status_async() == sl.ERROR_CODE.SUCCESS:
                                zed.retrieve_spatial_map_async(pymesh)
                               
                                                   
                        _, image22 = cv2.imencode('.JPEG', image2, [cv2.IMWRITE_JPEG_QUALITY, 90])
                        frame_data2 = pickle.dumps(image22)
                        frame_size2 = len(frame_data2)                  
                       
                        await websocket.send(frame_size2.to_bytes(4, byteorder='big'))
                        await websocket.send(frame_data2)
                       
                        '''
                        pymesh.update_mesh_from_chunklist()
                        print(pymesh.triangles)
                        image12 = convert_mesh_to_image(pymesh)
                        '''
                       
                        '''
                        _ , encoded_frame = cv2.imencode('.JPEG', image12, [cv2.IMWRITE_JPEG_QUALITY, 90])
                        frame_data = pickle.dumps(encoded_frame)
                        frame_size = len(frame_data)
                        await websocket.send(frame_size.to_bytes(4, byteorder='big'))
                        await websocket.send(frame_data)
                        '''
                       
                        #print(mapping_state)
                        save_count += 1
                       
                        print(save_count)
                        #if mapping_state == sl.SPATIAL_MAPPING_STATE.NOT_ENOUGH_MEMORY:
                        if save_count == 1000:    
                            i = i % 5	
                            print('save')
                         
                            zed.extract_whole_spatial_map(pymesh)

                            filter_params = sl.MeshFilterParameters()
                            filter_params.set(sl.MESH_FILTER.LOW)
                            pymesh.filter(filter_params, True)
                           
                            '''
                            if spatial_mapping_parameters.save_texture:
                                print("Save texture set to : {}".format(spatial_mapping_parameters.save_texture))
                                pymesh.apply_texture(sl.MESH_TEXTURE_FORMAT.RGBA)        
                            '''
                           

                            filepath = "mesh_gen" + str(i) + ".obj"                                                    
                           
                            #filepath = "mesh_gen.obj"
                            status = pymesh.save(filepath)
                            save_count = 0
                            #pymesh.clear()
                           
                            i += 1
                           
                            subprocess.run(['python3', '/home/wook/Capston/objsender.py',  str(i-1)])
                            #subprocess.run(['python3', '/home/wook/Capston/objsender.py'])
                            #pymesh.clear()
                           
                           
                         
   
            image.free(memory_type=sl.MEM.CPU)
            pymesh.clear()
            zed.disable_spatial_mapping()
            zed.disable_positional_tracking()
            zed.close()
           
        except(websockets.ConnectionClosed):
            pass
       
           
       
if __name__ == "__main__":
    asyncio.get_event_loop().run_until_complete(main_async())