import subprocess


def parse_shot_info(input_string):
    result_dict = {"live": [], "queue": []}

    # Split the input string by commas to separate individual shot info
    shot_info_list = input_string.split(', ')

    # Initialize variables to keep track of the current shot name, live status, and queue status
    current_shot_name = None
    is_live = False
    is_queue = False

    for shot_info in shot_info_list:
        # Split each shot info by colon to separate key and value
        key, value = shot_info.split(':')

        # Clean up the key and value
        key = key.strip()
        value = value.strip()

        if key == "shotName":
            # Update the current shot name
            current_shot_name = value
        elif key == "isLive":
            # Update the live status
            is_live = (value == "true")
        elif key == "isPreview":
            # Update the queue status
            is_queue = (value == "true")

            # Add the current shot name to the appropriate list based on live/queue status
            if is_live:
                result_dict["live"].append(current_shot_name)
            elif is_queue:
                result_dict["queue"].append(current_shot_name)

    return result_dict


def get_mac_wirecast_shots():
    script = '''
    on run
    	-- Get the Live shot on the normal Layer
    	return GetLivePreviewShot(2)
    end run

    on GetLivePreviewShot(layer_index)
    	set output to {}
    	tell application "Wirecast"
    		-- Obtain Live and Preview Shots
    		set myDoc to last document
    		set myLayer to layer layer_index of myDoc
    		set myLiveShot to live shot of myLayer
    		set myPreviewShot to preview shot of myLayer

    		-- Show Live/Preview status of Live shot
    		set shotName to name of myLiveShot
    		set isLive to live of myLiveShot
    		set isPreview to preview of myLiveShot

    		set liveOutput to {shotName:shotName, isLive:isLive, isPreview:isPreview}
    		set end of output to liveOutput

    		-- Show Live/Preview of Preview Shot
    		set shotName to name of myPreviewShot
    		set isLive to live of myPreviewShot
    		set isPreview to preview of myPreviewShot

    		set previewOutput to {shotName:shotName, isLive:isLive, isPreview:isPreview}
    		set end of output to previewOutput
    	end tell
    	return output
    end GetLivePreviewShot
    '''
    result = subprocess.run(['osascript', '-e', script], capture_output=True, text=True)
    if result.returncode == 0:
        return parse_shot_info(result.stdout)
    else:
        print("Error running AppleScript:")
        print(result.stderr)
        return None


if __name__ == "__main__":
    output = get_mac_wirecast_shots()
    if output is not None:
        print(output)

    else:
        print("Failed to retrieve shot information.")
