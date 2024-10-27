import streamlit as st
import string

def isin_check(x):
    try:
        code = str(x)

        def transco_isin(x):
            x = str(x)
            AZ = string.ascii_uppercase
            AZ = [i for i in AZ]
            if x in AZ:    
                for i, y in enumerate(AZ, 10):
                    if y == x:
                        return i
            else:
                return int(x)

        def func(x):
            a = []
            for i in range(len(x)):
                if i % 2 == 0:
                    a.append(2)
                else:
                    a.append(1)
            return a

        def boarder(x):
            for i in range(x, x + 11):
                if i % 10 == 0:
                    return i

        code_transco = [str(transco_isin(i)) for i in code]
        code_transco = ''.join(code_transco)
        end_code = code_transco[-1]
        start_code = code_transco[:-1]

        IP = func(start_code)
        start_code = [int(i) for i in start_code]
        matrix = [a * b for a, b in zip(start_code, IP)]
        matrix = [str(i) for i in matrix]
        matrix = ''.join(matrix)
        matrix = [int(i) for i in matrix]

        sum_isin = sum(matrix)

        if int(boarder(sum_isin)) - int(sum_isin) - int(end_code) == 0:
            return True
        else:
            return False

    except ValueError:
        return False

# Streamlit app
st.title("ISIN Code Validator")
st.write("Enter an ISIN code to check if it's valid.")

# User input for ISIN code
user_input = st.text_input("Enter ISIN code:", "")

# Validate the ISIN code when the button is clicked
if st.button("Validate"):
    if user_input:
        # Perform the ISIN check
        is_valid = isin_check(user_input)
        
        # Display the result
        if is_valid:
            st.success(f"The ISIN code '{user_input}' is valid.")
        else:
            st.error(f"The ISIN code '{user_input}' is not valid.")
    else:
        st.warning("Please enter an ISIN code.")