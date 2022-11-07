import cv2
import numpy as np
from colormath.color_objects import sRGBColor, LabColor
from colormath.color_conversions import convert_color
from colormath.color_diff import delta_e_cie2000


def main():
    #-------- Load parameters --------
    # TODO: All this should be loaded from a config file, or interactively.
    image_path = './media/original_image.jpeg'

    # Below are  values for the sample image. Change them according
    # to your image, as described in the readme.

    # Start and end position of heatmap
    x_start = 18
    y_start = 10

    x_end = 469
    y_end = 593


    # Cells in heatmap
    n, m = 13, 8

    # Legend position
    x_legend = 514
    y_legend_bottom =  580 # bottom visual position of legend
    y_legend_top = 10

    # Legend min and max values
    legend_min = 0
    legend_max = 25

    number_of_legend_steps = 25 # Not necessarily same as number of legend steps

    #-------- Load image --------
    image = cv2.imread(image_path)


    #-------- Common values used later --------
    legend_value_step = (legend_max - legend_min) / number_of_legend_steps
    legend_step_size = (y_legend_bottom - y_legend_top) / number_of_legend_steps

    heatmap_step_y = (y_end - y_start)/n
    heatmap_step_x = (x_end - x_start)/m

    heatmap_offset_x = heatmap_step_x/2
    heatmap_offset_y = heatmap_step_y/2


    #-------- From legend, generate color -> value mapping --------
    color_value_map = {}
    legend_y_coordinates = []
    for i in range(number_of_legend_steps+1):
        legend_y_coordinate = round(y_legend_bottom - i * legend_step_size)
        legend_y_coordinates.append(legend_y_coordinate)

        # Note: numpy expects (y,x) coordinates
        coordinate = (legend_y_coordinate, x_legend)
        rgb = image[coordinate]
        value_to_be_mapped = round(legend_min + i * legend_value_step)

        tuple = (rgb[0], rgb[1], rgb[2])
        color_value_map[tuple] = value_to_be_mapped

        print(f'Legend coordinate {coordinate} has RGB value {rgb} and value {value_to_be_mapped}')

    # Debug:
    for k,v in color_value_map.items():
        print(f'Key {k} has value {v}')


    #-------- Calculate center positions of heatmap cells --------
    heatmap_cells_center_coordinates = []

    for i in range(n):
        heatmap_y = round(y_start + i * heatmap_step_y + heatmap_offset_y)
        for j in range(m):
            heatmap_x = round(x_start + j * heatmap_step_x + heatmap_offset_x)
            heatmap_cells_center_coordinates.append((heatmap_y, heatmap_x))

    # Debug: print values of heatmap cells
    for i in range(n):
        for j in range(m):
            index = i*m +j
            coordinate = heatmap_cells_center_coordinates[index]
            print(coordinate, end=' ')
        
        print('')

    #-------- RGB -> value --------
    def get_heatmap_value(rgb, color_value_map):
        """
        Euclidian distance doesn't work.
        Using Lab color space to find the closest color in the color map.
        https://dev.to/tejeshreddy/color-difference-between-2-colours-using-python-182b
        """
        min_dist = 1e20
        return_value = None
        
        color1_rgb = sRGBColor(rgb[0], rgb[1], rgb[2])
        color1_lab = convert_color(color1_rgb, LabColor)

        for k,v in color_value_map.items():
            color2_rgb = sRGBColor(k[0], k[1], k[2])
            color2_lab = convert_color(color2_rgb, LabColor)
            dist = delta_e_cie2000(color1_lab, color2_lab)
            if dist < min_dist:
                min_dist = dist
                return_value = v
        
        return return_value

    #-------- Extract values --------
    # Get heatmap values
    heatmap_values = np.zeros((n,m))

    for i in range(n):
        for j in range(m):
            index = i*m +j
            coordinate = heatmap_cells_center_coordinates[index]
            rgb = image[coordinate]
            heatmap_values[i,j] = get_heatmap_value(rgb, color_value_map)

    #-------- Save values --------
    # TODO: Save to file, or print to console
    print(heatmap_values)


    #-------- Visualize values --------
    # Visualize legend
    for i, legend_y_coordinate in enumerate(legend_y_coordinates):
        image[legend_y_coordinate, x_legend] = (0, 0, 255)
        cv2.putText(img= image, text=str(i + legend_min), org = (x_legend+5, legend_y_coordinate), fontFace = cv2.FONT_HERSHEY_SIMPLEX, fontScale = 0.5, color = (0,0,255), thickness = 1)

    # Visualize extracted values
    for i in range(n):
        for j in range(m):
            index = i*m +j
            coordinate = heatmap_cells_center_coordinates[index]
            value = heatmap_values[i,j]
            cv2.putText(img= image, text=str(value), org = (coordinate[1], coordinate[0]), fontFace = cv2.FONT_HERSHEY_SIMPLEX, fontScale = 0.5, color = (0,0,255), thickness = 1)

    cv2.imshow('Image with legend', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()