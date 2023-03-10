import sqlite3,sys

def add_image_to_database(image_path,id,name,description,count):
    with sqlite3.connect("..\db_directory\mydatabase.sqlite3") as conn:
        cursor = conn.cursor()
        with open(image_path, 'rb') as file:
            image_blob = file.read()
        cursor.execute("INSERT INTO badges(badge_image, badge_id,badge_name,badge_description,badge_count_required) VALUES (?,?,?,?,?)", (image_blob,id,name,description,count))
        conn.commit()




if __name__ == "__main__":
    image_path = input("Enter the path to the image file: ")
    id = input("Enter the badge id: ")
    name = input("Enter the badge name: ")
    description = input("Enter the badge description: ")
    count = input("Enter the badge count: ")

    add_image_to_database(image_path, id, name, description, count)
    print("Image added to database.")