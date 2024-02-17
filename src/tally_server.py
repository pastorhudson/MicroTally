import aiohttp
import asyncio
from utils import build_camera_config, build_camera_state, get_wirecast_shots, setup_logger
import logging


CAMERA_CONFIG = build_camera_config()
# Assuming this dict to keep track of the current state of each camera
# This is a simplified state management approach
CAMERA_STATE = build_camera_state()


async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            html = await response.text()


async def change_cam(camera_name, cam_status):
    cam_ip = CAMERA_CONFIG.get(camera_name)
    if cam_ip:
        url = f"http://{cam_ip}/?led={cam_status}"
        await fetch(url)
    else:
        print(f"Camera {camera_name} not found in configuration.")


async def handle_tally(camera, status):
    tasks = []
    if status == 'queue':
        # If setting a camera to queue, turn off any other queued cameras, but keep the live one as is
        for cam_name, cam_status in CAMERA_STATE.items():
            if cam_name != camera and cam_status == 'queue':
                tasks.append(change_cam(cam_name, 'off'))
                CAMERA_STATE[cam_name] = 'off'
        tasks.append(change_cam(camera, 'queue'))  # Queue the specified camera

    elif status == 'live':
        # If setting a camera to live, set all others to off
        for cam_name in CAMERA_CONFIG.keys():
            if cam_name != camera:
                tasks.append(change_cam(cam_name, 'off'))
                CAMERA_STATE[cam_name] = 'off'

        tasks.append(change_cam(camera, 'live'))  # Set the specified camera to live

    elif status == 'off':
        # Just turn off the specified camera without affecting others
        tasks.append(change_cam(camera, 'off'))
        CAMERA_STATE[camera] = 'off'

    # Run all the tasks concurrently
    await asyncio.gather(*tasks)


async def all_off():
    for cam in CAMERA_STATE:
        await handle_tally(cam, 'off')


async def run_tallys(logger):
    # logger = setup_logger('microtally', level=logging.INFO)

    await all_off()
    while True:
        shots = get_wirecast_shots()
        for shot_type, shots in shots.items():
            logger.debug(f"{shot_type}, {shots}")
            logger.debug(CAMERA_STATE)
            if shot_type == 'queue' and not shots:
                logger.debug('Nothing Queued!')
                for cam, cam_state in CAMERA_STATE.items():
                    logger.debug(f"{cam}, {cam_state}")
                    if cam_state == 'queue':
                        await handle_tally(cam, "off")

            for shot in shots:
                if shot.lower() in CAMERA_CONFIG and CAMERA_STATE[shot.lower()] != shot_type:
                    logger.info(f"Updating: {shot.lower()} to {shot_type}")
                    CAMERA_STATE[shot.lower()] = shot_type
                    await handle_tally(shot.lower(), shot_type)
                else:
                    logger.debug('skipping no updates')
        await asyncio.sleep(.1)

    # Example usage
    # print(CAMERA_STATE)
    # await handle_tally('right', 'off')  # This will queue left_cam and turn off any other camera that might be in 'queue'
    # await handle_tally('right_cam', 'live')  # This will set center_cam to 'live' and others to 'off'

if __name__ == "__main__":

    logger = setup_logger('microtally', level=logging.INFO)

    # Run the main function
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run_tallys())
