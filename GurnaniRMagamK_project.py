
"""

@author: kirtimagam
"""

import pymysql
import sys


def main():
    
    try:
        user = input("Please enter username: ")
        password = input("Please enter password: ")
        
        cnx = pymysql.connect(host='localhost', user= user, password = password,
                          db='recipes',charset='utf8mb4', 
                          cursorclass=pymysql.cursors.DictCursor, autocommit = True)
        
        cursor = cnx.cursor()
        
        user_type = input("What type of user are you? Type in member or moderator: ")

        if user_type.lower() == 'member':
            sign = input("Do you need to sign up as a member? Type in 'yes' or 'no': ")
      
            if sign.lower() == 'yes':
                name = input("Enter a profile name: ")
                email = input("Enter your email: ")
                username = input("Please create a username: ")
                passwrd = input("Please enter a password: ")
    
                # call stored procedure that adds to member table 
                params = (name, email, username, passwrd)
                cursor.execute("call add_new_mem(%s, %s, %s, %s)", params)
    
                # get member_id
                params = (username, passwrd)
                cursor.execute("call member_id(%s, %s)", params)
                mem_id_lst = cursor.fetchall()
                mem_id_dict = mem_id_lst[0]
                mem_id = mem_id_dict["member_id"]
                
                print("You have been added as a member!")
                member_login = True
            
            if sign.lower() == 'no':
                member_login = False
                while True:
                    login_user = input("Please enter your member username: ")
                    login_pass = input("Please enter your member password: ")
                    params = (login_user, login_pass)
                    cursor.execute("call mem_exists(%s, %s)", params)
                    check = cursor.fetchall()
                                            
                    if len(check) > 0:
                        member_login = True
                        print("Congrats, login successful.")
        
                        # get member_id
                        params = (login_user, login_pass)
                        cursor.execute("call member_id(%s, %s)", params)
                        mem_id_lst = cursor.fetchall()
                        mem_id_dict = mem_id_lst[0]
                        mem_id = mem_id_dict["member_id"]
                        break
        
                    elif len(check) == 0:
                        print("Sorry, login unsuccessful. Please try again. ")
            
            while True:
                if member_login == True:
                    submit_action = input("Would you like to submit a recipe(Yes or No)? ")
                    if submit_action.lower() == "yes":
                        name = input("Please enter recipe title: ")
                        instructions = input("Please enter recipe instructions: ")
                        descrip = input("Please give a recipe description: ")
                        cuisine = input("Please enter recipe cuisine: ")
                        region = input("Please enter region that the cuisine belongs to: ")
                        time = input("Please enter time estimate for recipe in minutes: ")
      
                        # put into stored procedure to add to recipe table
                        recipe_params = (name, instructions, descrip, time, cuisine, mem_id, region)
                        cursor.execute("call add_recipe(%s, %s, %s, %s, %s, %s, %s)", recipe_params)
                        print("Congrats, your recipe was submitted for approval.")
      
                        # retrieve recipe_id to ask for ingredients and utensil details
                        cursor.execute("call r_id(%s)", name)
                        r_id_lst = cursor.fetchall()
                        r_id_dict = r_id_lst[0]
                        r_id = r_id_dict["r_id"]
                
                        utensils = input("Please list utensils needed, separated by commas: ")
                      
                        utensil_lst = utensils.split(",")
            
                        for i in range(len(utensil_lst)):
                            params = (utensil_lst[i], r_id)
                            cursor.execute("call add_utensil(%s, %s)", params)
                        print("Congrats, your utensils have been added for your recipe submission.")
                
                        ingred_name = input("Please list ingredients needed, separated by commas: ")
                        amt = input("Please list amounts corresponding to those ingredients"
                                    ", separated by commas: ")
                        
                        ingredients = ingred_name.split(",")
                        amt_lst = amt.split(",")
                
                        for i in range(len(ingredients)):
                            i_params = (ingredients[i], amt_lst[i], r_id)
                            cursor.execute("call add_ingred(%s, %s, %s)", i_params)
                        print("Congrats, your ingredients have been added for your recipe submission.")
      
              # for search filter make sure status is approved when giving results
                    search_action = input("Would you like to search for recipes(Yes or No)? ")
                    if search_action.lower() == "yes":
                        name_filter = input("Would you like to search by name(Yes or No)? ")
                        if name_filter.lower() == "yes":
                            while True:
                                name = input("Please type recipe name for search: ")
                                cursor.execute("call search_name(%s)", name)
                                name_recipe = list(cursor.fetchall())
                                print(name_recipe)
                                if len(name_recipe) < 1:
                                    print("Name is not in database. Try again. ")
                                else:
                                    break
                        
                        keyword_filter = input("Would you like to search by keyword(Yes or No)? ")
                        if keyword_filter.lower() =="yes":
                            keyword = input("Please input keyword for search: ")
                            keyword = "%" + keyword + "%"
                            cursor.execute("call search_keyword(%s)", keyword)
                            keyword_recipes = list(cursor.fetchall())
                            print(keyword_recipes)
                            
                            
                        cuisine_filter = input("Would you like to search by cuisine(Yes or No)? ")
                        if cuisine_filter.lower() == "yes":
                            # stored procedure to return list of current cuisines to guide search
                            cuisine_select =  "select name from cuisine "
                            cursor.execute(cuisine_select)
                            cuisines = cursor.fetchall()
                            
                            cuisine_lst = []
                            for c in cuisines:
                                cuisine_lst.append(c["name"].lower())
                            print(cuisine_lst)
                            while True:
                                cuisine = input("Please type cuisine for search: ").lower()
                                if cuisine not in cuisine_lst:
                                    print("Please retry with a different cuisine.")
                                else:
                                  # stored procedure to return list of cuisines with that name
                                  cursor.execute("call search_cuisine(%s)", cuisine)
                                  cuisine_recipes = cursor.fetchall()
                                  break
          
                            print("Cuisine Search Results: ")
                            print(cuisine_recipes)
        
                                
                        time_filter = input("Would you like to search by time est(Yes or No)? ")
                        if time_filter.lower() == "yes":
                            time_est = int(input("Please enter approx. time in minutes: "))
                            # call stored procedure that gets recipes within 10 min range of time given
                            # make sure to convert hours to minutes in stored procedure if necessary
                            cursor.execute("call search_time(%s)", time_est)
                            time_recipes = list(cursor.fetchall())
                    
                            print("Time Est Search Results: ")
                            for row in time_recipes:
                              print(row)
      
                    select_action = input("Would you like to select a recipe from your search(Yes or No? ")
                    if select_action.lower() == "yes":
                        # display the list of recipes from their search 
                        recipe = int(input("Please enter recipe id of desired recipe from search: "))
                        # return recipe details as well as utensils and ingredients associated with it
                        cursor.execute("call recipe_details(%s)", recipe)
                        recipe_details = list(cursor.fetchall())
              
                        cursor.execute("call recipe_utensils(%s)", recipe)
                        recipe_utensils = list(cursor.fetchall())
      
                        cursor.execute("call recipe_ingred(%s)", recipe)
                        recipe_ingredients = list(cursor.fetchall())
      
                        print("Recipe Details:")
                        print(recipe_details)
                        print()
                        print("Recipe Ingredients:")
                        print(recipe_ingredients)
                        print()
                        print("Recipe Utensils:")
                        print(recipe_utensils)
                        
                    submit_count_act = input("Would you like to know how many"
                                             " recipe submissions you have(Yes"
                                             " or No)? ")
                    if submit_count_act.lower() == "yes":
                        cursor.execute("call initialize_count_sub")
                        
                        cursor.execute("call count_of_sub(%s)", mem_id)
                        sub_count = cursor.fetchall()
                        print("submission count: ", sub_count)
      
                    next_action = input("Would you like to continue submit/search(Yes or No)? ")
                    if next_action.lower() == "yes":
                        print("You will be redirected.")
                    else:
                        member_login = False
                        print("Logging user out.")
                        break
    
        elif user_type.lower() == 'moderator':
            mod_sign = input("Do you need to sign up as a moderator? Type in 'yes' or 'no': ")
            if mod_sign.lower() == 'yes':
                mod_name = input("Enter a profile name: ")
                mod_email = input("Enter your email: ")
                mod_username = input("Please create a username: ")
                mod_passwrd = input("Please enter a password: ")
    
                # call stored procedure that adds to moderator table 
                mod_reg = (mod_name, mod_email, mod_username, mod_passwrd)
                cursor.execute("call add_new_mod(%s, %s, %s, %s)", mod_reg)
                
                # get mod id
                params = (mod_username, mod_passwrd)
                cursor.execute("call mod_id(%s, %s)", params)
                mod_id_lst = cursor.fetchall()
                mod_id_dict = mod_id_lst[0]
                mod_id = mod_id_dict["moderator_id"]
                
                print("You have been added as a moderator!")
                mod_login = True
          
      
      
            if mod_sign.lower() == 'no':
                mod_login = False
                while True:
                    login_user = input("Please enter your moderator username: ")
                    login_pass = input("Please enter your moderator password: ")
    
                    # check if user and password exist in moderator table (possibly w/ function)
                    params = (login_user, login_pass)
                    cursor.execute("call mod_exists(%s, %s)", params)
                    check = cursor.fetchall()
                    if len(check) > 0:
                        mod_login = True
                        print("Congrats, login successful.")
                        # get mod id
                        params = (login_user, login_pass)
                        cursor.execute("call mod_id(%s, %s)", params)
                        mod_id_lst = cursor.fetchall()
                        mod_id_dict = mod_id_lst[0]
                        mod_id = mod_id_dict["moderator_id"]
                        break
                    elif len(check) == 0:
                        print("Sorry, login unsuccessful. Please try again. ")
            if mod_login == True:
                mod_action = input("Type 'view' if you would like to review the " +
                                    "submitted recipes waiting for approval: ")
                if mod_action.lower() == 'view':
                    #use sql to return recipes with submitted
                    stmt_select =  "select * from recipe where status = 'Submitted'"
                    cursor.execute(stmt_select)
                    sub_recipes = cursor.fetchall()
         
                    # use while loop
                    for recipe in sub_recipes:
                        while True:
                            print(recipe)
                            mod_res = input("Do you 'approve' or 'deny' this recipe: ")
        
                            if mod_res.lower() == 'approve':
                                recipe_id = recipe["r_id"]
                                cursor.execute("call change_status(%s, %s)", (recipe_id, mod_id)) 
                                break
        
                            elif mod_res.lower() == 'deny':
                                #call procedure to delete
                                recipe_id = recipe["r_id"]
                                cursor.execute("call delete_recipe(%s)", recipe_id)
                                break
        
                            else:
                                print("Invalid response. Type in approve or deny.")
                mod_login = False
                print("Logging out moderator. ")
    
    
    
    except Exception as e:
        exception_type, exception_object, exception_traceback = sys.exc_info()
        filename = exception_traceback.tb_frame.f_code.co_filename
        line_number = exception_traceback.tb_lineno
        
        print("Exception type: ", exception_type)
        print(e)
        print("File name: ", filename)
        print("Line number: ", line_number)
        
    finally:
        cursor.close()
        cnx.close()
        
main()