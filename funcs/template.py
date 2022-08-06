from PIL import Image
import os


def saveTemplate(name, img, coords, canvas, factionID):
    """Saves a template in the faction path.
    name -> str
    img -> PIL Object
    coords -> array with x & y
    canvas -> str as e, 1 or m
    factionID -> str of the faction ID"""
    factionPath = None
    for i in os.listdir(r'./factions/'):
        if i.startswith(f'{factionID}'):
            factionPath = i
        else:
            pass
    imgPath = f'./factions/{factionPath}/_{name}_{coords[0]}_{coords[1]}_{canvas}_.png'
    if factionPath is None:
        return 0
    if not os.path.exists(imgPath):
        img.save(imgPath)
        return 2
    else:
        return 1
