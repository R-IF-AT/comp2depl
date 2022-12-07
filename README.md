# comp2depl
parser: python3 cdxmi.py -i component.xmi -l hw.csv

solver: pip install pyomo
        pip install pandas
        python3 main.py

drawer: ./gradlew draw