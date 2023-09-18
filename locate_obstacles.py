import argparse, os
from PIL import Image, ImageDraw

# Takes contents of map description file
# Returns size of the map, cell size and obstacles' descriptions
def extract_map_information(file_contents):
    lines = file_contents.split('\n')
    width, height, s = map(int, lines[0].split())
    n_of_obstacles = int(lines[1])
    obstacles = [list(map(int, lines[i + 2].split())) for i in range(n_of_obstacles)]
    return width, height, s, obstacles


# Throws errors if input is invalid
def validate_input(width, height, s, obstacles, robot_x, robot_y):
    if width < 1 or height < 1:
        raise Exception("map dimensions should be positive")
    if s < 1:
        raise Exception("cell size should be positive")
    
    for obs in obstacles:
        if len(obs) != 4:
            raise Exception(f"{str(obs)} is not valid obstacle description")
        x1, y1, x2, y2 = obs
        for coord in [x1, x2]:
            if coord < 0 or coord > width * s or coord % s != 0:
                raise Exception(f"{str(obs)} describe invalid obstacle")
        for coord in [y1, y2]:
            if coord < 0 or coord > height * s or coord % s != 0:
                raise Exception(f"{str(obs)} describe invalid obstacle")
    
    if robot_x < 0 or robot_x > width * s or robot_y < 0 or robot_y > height * s:
        raise Exception(f"Invalid robot position ({str(robot_x)}, {str(robot_y)})")


# Draws the map and shows it    
def draw_map(width, height, s, obstacles, robot_x, robot_y, closest):
    cell_size_px = 100
    width_px = width * cell_size_px
    height_px = height * cell_size_px

    def get_px_coord(coord):
        return coord / s * cell_size_px

    image = Image.new("RGB", (width_px + 1, height_px + 1), "white")
    draw = ImageDraw.Draw(image)

    # Draw grid
    for i in range(height + 1):
        draw.line([(0, i * cell_size_px), (width_px, i * cell_size_px)], fill="black")
    for i in range(width + 1):
        draw.line([(i * cell_size_px, 0), (i * cell_size_px, height_px)], fill="black")

    # Draw obstacles
    for obs in obstacles:
        draw.rectangle(list(map(get_px_coord, obs)), fill="black")

    # Draw robot
    draw.regular_polygon((get_px_coord(robot_x), get_px_coord(robot_y), cell_size_px / 10), 4, fill="red", rotation=45)

    # Draw lines to closests obstacles
    for angle, coords in closest.items():
        draw.line([(get_px_coord(robot_x), get_px_coord(robot_y)), tuple(map(get_px_coord, coords))], fill="green", width=2)
        draw.regular_polygon((tuple(map(get_px_coord, coords)), cell_size_px / 20), 100, fill="green")

    if not os.path.isdir("output"):
        os.makedirs("output")
    image.save("output/visualization.png")


# Returns a dictionary with the closests obstacles to the robot in 4 directions
def find_closests(width, height, s, obstacles, robot_x, robot_y):
    closests = {0: [robot_x, 0], 90: [width * s, robot_y], 180: [robot_x, height * s], 270: [0, robot_y]}

    for x1, y1, x2, y2 in obstacles:
        if robot_x <= x1:
            if y1 <= robot_y and robot_y <= y2:
                closests[90][0] = min(closests[90][0], x1)
        elif x2 <= robot_x:
            if y1 <= robot_y and robot_y <= y2:
                closests[270][0] = max(closests[270][0], x2)
        else:
            if robot_y <= y1:
                closests[180][1] = min(closests[180][1], y1)
            elif y2 <= robot_y:
                closests[0][1] = max(closests[0][1], y2)
            else:
                closests[0] = [robot_x, robot_y]
                closests[90] = [robot_x, robot_y]
                closests[180] = [robot_x, robot_y]
                closests[270] = [robot_x, robot_y]
    
    return closests


def main():
    # Parse the command line arguments
    parser = argparse.ArgumentParser(description='Draws the map using input file, robot position. Calculates closest obstacles to the robot from each direction')
    parser.add_argument('file_path', type=str, help='Path to the file with the map')
    parser.add_argument('robot_x', type=float, help='Coordinate x of the robot (float)')
    parser.add_argument('robot_y', type=float, help='Coordinate y of the robot (float)')
    args = parser.parse_args()

    try:
        with open(args.file_path, 'r') as file:
            # Main functionality
            width, height, s, obstacles = extract_map_information(file.read())
            validate_input(width, height, s, obstacles, args.robot_x, args.robot_y)
            closests = find_closests(width, height, s, obstacles, args.robot_x, args.robot_y)
            draw_map(width, height, s, obstacles, args.robot_x, args.robot_y, closests)
            for angle, coords in closests.items():
                print(f"{str(angle)}: ({str(coords[0])}, {str(coords[1])})")

    except FileNotFoundError:
        print(f"Error: The file '{args.file_path}' does not exist.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == '__main__':
    main()
