from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
from PIL.ExifTags import TAGS
import hachoir
from hachoir.parser import createParser
from hachoir.core.i18n import getTerminalCharset
from hachoir.core.tools import makePrintable
from os import walk, path
import os
import time
import sys

import hachoir.metadata

# App Config
pic_dir = 'C:/Users/every/Pictures/Photography/Edited/'
output_folder = '/.metariser/'
app_name = "ALLEN Metariser"
app_url = "www.hallen.uk/project/metariser"

print(" ")
print("ALLEN Metariser")
print(f"© {time.localtime().tm_year} Harold Allen. All rights reserved.")
print(" ")
print(app_url)
print(" ")

# User Config
folder = input('Enter the folder name: ')
if sys.argv.count('--custom') > 0 or sys.argv.count('-c') > 0:
    config_border = input('Border? (y/n): ').lower() == 'y'
    config_meta = input('Metadata image? (y/n): ').lower() == 'y'
    watermark = input(f"Copyright (blank for none): © ")
else:
    config_border = True
    config_meta = True
    watermark = ""

start_time = time.time()

f = []
for (dirpath, dirnames, filenames) in walk(pic_dir + folder):
    f.extend(filenames)
    break

for file in f:
    # Record start time for file
    file_start_time = time.time()
    
    # Open image
    old_im = Image.open(pic_dir + folder + "/" + file)
    meta_im = old_im.copy()
    
    # Get border and size units (border is double the actual border size)
    old_size = old_im.size
    border = min(old_im.size[0] // 10, old_im.size[1] // 10)
    y_unit = old_im.size[1] // 15

    if config_border:
        # Add border
        new_size = (old_im.size[0] + border, old_im.size[1] + border)
        new_im = Image.new("RGB", new_size, "White")
        box = tuple((n - o) // 2 for n, o in zip(new_size, old_size))
        new_im.paste(old_im, box)
    else:
        new_size = old_size
        new_im = old_im
        
    if path.exists(pic_dir + folder + output_folder) == False:
        os.makedirs(pic_dir + folder + output_folder)
    new_im.save(pic_dir + folder + output_folder + file)
        
    if config_meta:
        # Blur image, then optionally add border
        if config_border:
            info_im = Image.new("RGB", new_size, "White")
        
            blurred_im = old_im.filter(ImageFilter.GaussianBlur(24))
            enhancer = ImageEnhance.Brightness(blurred_im)
            blurred_im = enhancer.enhance(0.66)
            
            info_im.paste(blurred_im, box)
        else:
            info_im = old_im.filter(ImageFilter.GaussianBlur(24))
            enhancer = ImageEnhance.Brightness(info_im)
            info_im = enhancer.enhance(0.66)
        
        # Set up text drawing
        draw = ImageDraw.Draw(info_im)
        font_dir = "C:/Users/every/AppData/Local/Microsoft/Windows/Fonts/Inter-VariableFont_slnt,wght.ttf"
        font_main = ImageFont.truetype(font_dir, y_unit*1.5)
        font_camera = ImageFont.truetype(font_dir, y_unit*0.66)
        font_icon = ImageFont.truetype(font_dir, y_unit*0.75)
        font_watermark = ImageFont.truetype(font_dir, y_unit*0.33)
        text_color = (255, 255, 255)
        
        parser = createParser(file, pic_dir + folder + "/" + file)
        if not parser:
            print(f"Unable to parse file {file}")
            continue
        else:
            try:
                metadata = hachoir.metadata.extractMetadata(parser)
            except err:
                print(f"Metadata extraction error: {err}")
            if not metadata:
                print("Unable to extract metadata")
                continue
            
            text = metadata.exportPlaintext()
            charset = getTerminalCharset()
            
            last_y = 0
            lens = False
            
            for index, line in enumerate(text):
                font = font_main
                size = round(font.size)
                main_size = size
                icon_y_offset = y_unit*0.2
                
                x = round(border*1.125+size+y_unit/3)
                
                if config_border == False:
                    x = border/2+size+y_unit/3
                
                icon_x = round(x-size-y_unit/3)
                
                if "Camera focal" in line:
                    metaline = "f/"+line[16:]
                    icon = Image.open("C:/Users/every/Dev/PhotoPrettier/icons/aperture.png")
                    y = border
                elif "Camera exposure" in line:
                    metaline = line[19:]
                    icon = Image.open("C:/Users/every/Dev/PhotoPrettier/icons/clock.png")
                    y = border+(main_size+y_unit/3)
                    
                    unit_x = x+font.getlength(metaline)+y_unit/6
                    draw.text((unit_x, y+font.size-font_camera.size*1.1), "sec", fill=text_color, font=font_camera)
                elif "ISO speed rating" in line:
                    metaline = line[20:]
                    icon = Image.open("C:/Users/every/Dev/PhotoPrettier/icons/sun.png")
                    y = border+(main_size+y_unit/3)*2
                    
                    unit_x = x+font.getlength(metaline)+y_unit/6
                    draw.text((unit_x, y+font.size-font_camera.size*1.1), "ISO", fill=text_color, font=font_camera)
                elif "Focal length" in line:
                    metaline = line[16:]
                    icon = Image.open("C:/Users/every/Dev/PhotoPrettier/icons/crosshair.png")
                    y = border+(main_size+y_unit/3)*3
                    
                    unit_x = x+font.getlength(metaline)+y_unit/6
                    draw.text((unit_x, y+font.size-font_camera.size*1.1), "mm", fill=text_color, font=font_camera)
                elif "Camera model" in line:
                    metaline = line[16:]
                    icon = Image.open("C:/Users/every/Dev/PhotoPrettier/icons/camera.png")
                    icon_y_offset = y_unit*0.07
                    font = font_camera
                    size = round(font.size)
                    icon_x = round(x-size-y_unit/3)
                    
                    y = border+(main_size+y_unit/3)*4+y_unit/6
                elif "Lens model" in line or index == len(text)-1:
                    if "Lens model" in line:
                        metaline = line[15:]
                    elif sys.argv.count('--lens') > 0 or sys.argv.count('-l') > 0:
                        metaline = input(f"Enter lens model for {file}: ")
                    else:
                        continue
                    
                    icon = Image.open("C:/Users/every/Dev/PhotoPrettier/icons/search.png")
                    icon_y_offset = y_unit*0.07
                    font = font_camera
                    size = round(font.size)
                    icon_x = round(x-size-y_unit/3)
                    lens = True
                    
                    y = border+(main_size+y_unit/3)*4+size+y_unit/3
                else:
                    continue
                
                icon = icon.resize((size, size), Image.Resampling.BICUBIC)
                
                info_im.paste(icon, (icon_x, round(y+icon_y_offset)), icon)
                draw.text((x, y), metaline, fill=text_color, font=font)
                
                last_y = y
            
            # Copyright
            if watermark != '':
                icon_x = round(x-font_camera.getlength("©")-y_unit/3)
                icon_y_offset = y_unit*0.06
                if lens:
                    y = last_y+font_camera.size+y_unit/6
                else:
                    y = last_y+(font_camera.size*3)+y_unit/1.25
                
                draw.text((icon_x, round(y-icon_y_offset)), "©", fill=text_color, font=font_icon)
                draw.text((x, y), watermark, fill=text_color, font=font_camera)
            
            # Metariser Watermark
            draw.text((border, new_size[1]-border-font_watermark.size*2-y_unit/6), f"Generated by {app_name}", fill=text_color, font=font_watermark)
            draw.text((border, new_size[1]-border-font_watermark.size), app_url, fill=text_color, font=font_watermark)
            
            info_im.save(pic_dir + folder + output_folder + file[:-3] + 'meta.jpg')
    
    file_time = time.time() - file_start_time
    
    print(f"Finished with {file} in {round(file_time*10)/10}s")
    
time = time.time() - start_time

print(" ")
print(f"Done in {round(time*10)/10}s")