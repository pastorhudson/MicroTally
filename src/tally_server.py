import aiohttp
import asyncio
from utils import get_microtally_config

CAMERA_CONFIG = get_microtally_config()
# Assuming this dict to keep track of the current state of each camera
# This is a simplified state management approach
CAMERA_STATE = get_microtally_config()

async def fetch(url):
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            # print(f"Status: {response.status}")
            # print(f"Content-type: {response.headers['content-type']}")
            html = await response.text()
            # print(f"Body: {html[:100]}...")  # print the first 100 characters of the body response


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
        tasks.append(change_cam(camera, 'queue'))  # Queue the specified camera
    elif status == 'live':
        # If setting a camera to live, set all others to off
        for cam_name in CAMERA_CONFIG.keys():
            if cam_name != camera:
                tasks.append(change_cam(cam_name, 'off'))
        tasks.append(change_cam(camera, 'live'))  # Set the specified camera to live
    elif status == 'off':
        # Just turn off the specified camera without affecting others
        tasks.append(change_cam(camera, 'off'))

    # Run all the tasks concurrently
    await asyncio.gather(*tasks)


async def main():
    # Example usage
    await handle_tally('left_cam', 'live')  # This will queue left_cam and turn off any other camera that might be in 'queue'
    # await handle_tally('right_cam', 'live')  # This will set center_cam to 'live' and others to 'off'


# Run the main function
loop = asyncio.get_event_loop()
loop.run_until_complete(main())
