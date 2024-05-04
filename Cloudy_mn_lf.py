import carla
import math
import random
import time
import numpy as np
import cv2


def depth_camera_callback(image,data_dict):
    image.convert(carla.ColorConverter.LogarithmicDepth)
    data_dict['depthimage']= np.reshape(np.copy(image.raw_data), (image.height,image.width,4))

def main():
    client = carla.Client('localhost',2000)
    world = client.get_world()

    bp_lib=world.get_blueprint_library()
    spawn_points = world.get_map().get_spawn_points()

    weather = carla.WeatherParameters(
    cloudiness=80.0,
    fog_density=20.0,
    sun_altitude_angle=-90.0)
    world.set_weather(weather)

    vehicle_bp = bp_lib.find('vehicle.lincoln.mkz_2020')
    spawnPoint=carla.Transform(carla.Location(x=-8,y=-60, z=0.598),carla.Rotation())
    vehicle = world.try_spawn_actor(vehicle_bp, spawnPoint)

    #spawnPoint=carla.Transform(carla.Location(x=-8,y=-65, z=0.598),carla.Rotation(pitch=0.0, yaw=0.0, roll=0.000000))
    #vehicle_bp = bp_lib.find('vehicle.lincoln.mkz_2020')
    #vehicle = world.try_spawn_actor(vehicle_bp, spawnPoint)
    blueprintsWalkers = world.get_blueprint_library().filter("walker.pedestrian.*")
    pedestrian_bp = random.choice(blueprintsWalkers)
    spawnPoint=carla.Transform(carla.Location(x=2,y=-60, z=0.598),carla.Rotation(pitch=0.0, yaw=0.0, roll=0.000000))
    pedestrian = world.try_spawn_actor(pedestrian_bp,spawnPoint)

    spectator = world.get_spectator()
    transform =vehicle.get_transform()
    spectator.set_transform(transform)


    depth_camera_bp = bp_lib.find('sensor.camera.depth')
    camera_init_trans = carla.Transform(carla.Location(z=1.6, x=0.4))
    depth_camera = world.spawn_actor(depth_camera_bp, camera_init_trans,attach_to=vehicle)

    image_w = depth_camera_bp.get_attribute("image_size_x").as_int()
    image_h = depth_camera_bp.get_attribute("image_size_y").as_int()


    camera_data = {'depthimage': np.zeros((image_h, image_w,4))}
    depth_camera.listen(lambda image: depth_camera_callback(image,camera_data))
    vehicle.set_autopilot(False)

    cv2.namedWindow('Depth Camera', cv2.WINDOW_AUTOSIZE)
    cv2.imshow('Depth Camera', camera_data['depthimage'])
    cv2.waitKey(1)

    while True:
        cv2.imshow('Depth Camera', camera_data['depthimage'])

        if cv2.waitKey(1)==ord('q'):
            break
    depth_camera.stop()
    cv2.destroyAllWindows()
    client.reload_world()

if __name__ == '__main__':

    main()
