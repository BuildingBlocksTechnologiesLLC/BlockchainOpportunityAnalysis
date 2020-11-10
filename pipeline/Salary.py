#File to take in salary information and return cleaner salary format

def cleanSalary(salary):
    #salary work
    print("This is the salary for this job posting: ", salary)
    print("this is type of salary: ", type(salary))

    #salary cleaner parse
    if("to" in salary):
        num = salary.split("to")
        print("This is split salary", num)

        sal = []
        #clean up salary
        for elem in num:
            if(elem[0] == "$"):
                elem = elem[1:]
            if(elem == "to" or elem == ","):
                continue
            #print("This is elem before , split", elem)
            elem = elem.split(",")
            #print("This is elem after , split", elem)
            #print("This is elem[0]", elem[0])
            sal.append(elem[0])
            sal.append("K")
            #print("This is sal: ", sal)

        #print("$"+str(sal[0])+str(sal[1]), "-", "$"+str(sal[2])+str(sal[3]))
        return("$"+str(sal[0])+str(sal[1]), "-", "$"+str(sal[2])+str(sal[3]))


    elif("-" in salary):
        num = salary.split("-")
        print("This is split salary", num)
        
        sal = []
        #clean up salary
        for elem in num:
            if(elem[0] == "$"):
                elem = elem[1:]
            if(elem == "-" or elem == ","):
                continue
            #print("This is elem before , split", elem)
            elem = elem.split(",")
            #print("This is elem after , split", elem)
            #print("This is elem[0]", elem[0])
            sal.append(elem[0])
            sal.append("K")
            #print("This is sal: ", sal)

        #print("$"+str(sal[0])+str(sal[1])+ "-" +"$"+str(sal[2])+str(sal[3]))
        return("$"+str(sal[0])+str(sal[1])+ "-" +"$"+str(sal[2])+str(sal[3]))

    elif("," in salary):
        sal = []
        elem = salary
        if(elem[0] == "$"):
                elem = elem[1:]
            #print("This is elem before , split", elem)
        elem = elem.split(",")
            #print("This is elem after , split", elem)
            #print("This is elem[0]", elem[0])
        sal.append(elem[0])
        sal.append("K")
            #print("This is sal: ", sal)

        #print("$"+str(sal[0])+str(sal[1]))
        return("$"+str(sal[0])+str(sal[1]))