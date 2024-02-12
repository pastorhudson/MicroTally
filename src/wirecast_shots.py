from wirecastCOMAPI import PreviewShotID, LiveShotID, getName


def get_shots():
    preview_shot1 = PreviewShotID(1)
    live_shot1 = LiveShotID(1)
    preview_shot2 = PreviewShotID(2)
    live_shot2 = LiveShotID(2)
    return {"queued2": str(getName(preview_shot2)).lower(), "live2": str(getName(live_shot2)).lower(),
            "queued1": str(getName(preview_shot1)).lower(), "live1": str(getName(live_shot1)).lower()}


if __name__ == "__main__":
    pass
