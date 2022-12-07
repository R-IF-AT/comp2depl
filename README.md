# comp2depl
parser: python cdxmi.py -i component.xmi -l hw.csv

solver: pip install pyomo
        pip install pandas
        python main.py

drawer: ./gradlew draw