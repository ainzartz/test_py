# def outer_function(msg):
#     def inner_function():
#         print msg
#     return inner_function

# hi_func = outer_function('Hi')
# bye_func = outer_function('Bye')

# hi_func()
# bye_func()

# def decorator_function(original_function):  
#     def wrapper_function():  
#         return original_function()  
#     return wrapper_function  


# def display(): 
#     print ("Execute display fucntion") 

# decorated_display = decorator_function(display) 

# decorated_display()


# def decorator_function(original_function):
#     def wrapper_function():
#         print ("{} fucntion Before".format(original_function.__name__))
#         return original_function()
#     return wrapper_function


# def display_1():
#     print ("Fucntion display_1 ")


# def display_2():
#     print ("Fucntion display_1")

# display_1 = decorator_function(display_1)  #1
# display_2 = decorator_function(display_2)  #2

# display_1()
# print
# display_2()


# def decorator_function(original_function):
#     def wrapper_function():
#         print ("{} fucntion Before".format(original_function.__name__))
#         return original_function()
#     return wrapper_function

# @decorator_function
# def display_1():
#     print ("Fucntion display_1 ")

# @decorator_function
# def display_2():
#     print ("Fucntion display_2")


# display_1()
# print
# display_2()



def decorator_function(original_function):
    def wrapper_function(*args, **kwargs):
        print ("{} fucntion Before".format(original_function.__name__))
        return original_function(*args, **kwargs)
    return wrapper_function

@decorator_function
def display_1():
    print ("Fucntion display_1 ")

@decorator_function
def display_2():
    print ("Fucntion display_2")

@decorator_function
def display_3(name, age):
    print ("Fucntion display_3 ({},{})".format(name, age))


display_1()
print
display_2()
print
display_3('test', 25)
