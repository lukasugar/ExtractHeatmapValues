import argparse
import cv2

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--image_path', type=str, required=True)
    args = parser.parse_args()
    return args

def main():
    args = parse_args()
    
    image = cv2.imread(args.image_path)
    cv2.imshow('image', image)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

if __name__ == '__main__':
    main()