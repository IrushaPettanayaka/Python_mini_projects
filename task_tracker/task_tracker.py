#CLI task tracker
#should be able to add tasks, mark them as complete, and view pending tasks
#build a menu for the user to select options
#add tasks
#view pending tasks
#mark tasks as complete
#delete tasks
#validate user input
#organise tasks in fuctions
#github handoff

def display_menu():
    tasks = []
    while True:
        print("1. View tasks")
        print("2. Exit")
        print("3. Add task")

        menu_choice = input("Enter your choice: ")

        if menu_choice == "1":
            if not tasks:
                print("No tasks available.")
            else:
                print("Pending tasks:")
                for i, task in enumerate(tasks, start=1):
                    print(f"{i}. {task}")
        elif menu_choice == "2":
            break
        elif menu_choice == "3":
            title = input("Enter task title: ")
            tasks.append(title)
            print(f"Task '{title}' added.")
        else:
            print("Invalid choice. Please try again.")
            
    


display_menu()   