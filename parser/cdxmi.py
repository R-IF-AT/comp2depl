#-----------------------------------------------------
# python script that parses the UML Component diagram in xmi format and pulls relevant information
# usage : cdxmi.py -i <*.xmi> -l <*.csv>
#
# author : balu muthuvelu, balum@utexas.edu
#-----------------------------------------------------

import sys,re,os,glob,argparse,csv

def group_lines(source):
  buffer = list()
  startBuffering = False
  for line in source:
    if 'GRM:ResourceUsage' in line:
      startBuffering = ~startBuffering
      #print(line)
      if buffer:
        yield buffer
      buffer = [line]
    else:
      if startBuffering:
        buffer.append(line)
  yield buffer

def group_connector_lines(source):
  buffer = list()
  startBuffering = False
  for line in source:
    if 'ownedConnector' in line:
      startBuffering = ~startBuffering
      #print(line)
      if buffer:
        #buffer.append(line)
        yield buffer
      buffer = [line]
    else:
      if startBuffering:
        buffer.append(line)
  yield buffer

def group_component_lines(source):
  buffer = list()
  startBuffering = False
  for line in source:
    if 'packagedElement' in line:
      if 'TopComponent' in line:
        continue
      if '/packagedElement' in line and startBuffering==False:
        continue
      startBuffering = ~startBuffering
      #print(line)
      if buffer:
        #buffer.append(line)
        yield buffer
      buffer = [line]
    else:
      if startBuffering:
        #print(line)
        buffer.append(line)
  yield buffer

def main():
  parser = argparse.ArgumentParser('usage %prog ' + \
            '-i <input_file>' '-l <hardware_list>')
  parser.add_argument('-i', dest='input', \
                      help= 'specify input xmi file to process')
  parser.add_argument('-l', dest='hwlist', \
                      help= 'specify input hardware list file in csv format to process')

  args = parser.parse_args()

  if args.input == None:
    print(parser.usage)
    exit(1)
  elif args.hwlist == None:
    print(parser.usage)
    exit(1)
  else:
    input = args.input
    topContainer  = []
    hwlistrows    = []
    connectedPorts= []

    hwlistfile = open(args.hwlist)
    hwreaderobj = csv.reader(hwlistfile)
    for rows in hwreaderobj:
      if hwreaderobj.line_num == 1:
        continue  #skip row
      hwlistrows.append(rows)
    hwlistfile.close()

    #print(hwlistrows)

    with open(input, "r") as infile:
      for lines in group_component_lines(infile):
        if len(lines)>1:
          linedict = {}
          ports = list()
          for line in lines:
            if 'uml:Component' in line:
              #linedict['ports'] = list()
              xminameregex = re.compile(r'(.*)(name=")(.*?)(")')
              xminamemo = xminameregex.search(line)
              if xminamemo is not None:
                linedict['name'] = xminamemo.group(3) 
              xmiidregex = re.compile(r'(.*)(xmi:id=")(.*?)(")')
              xmiidmo = xmiidregex.search(line)
              if xmiidmo is not None:
                #print(xmiidmo.group(3))
                linedict['id'] = xmiidmo.group(3) 
            if 'uml:Port' in line:
              xmiidregex = re.compile(r'(.*)(xmi:id=")(.*?)(")')
              xmiidmo = xmiidregex.search(line)
              if xmiidmo is not None:
                #print(xmiidmo.group(3))
                ports.append(xmiidmo.group(3))
          linedict['ports'] = ports
          topContainer.append(linedict)

    with open(input, "r") as infile:
      for lines in group_lines(infile):
        #print(lines)
        if (lines[0].strip().startswith('<GRM')):
          execTime = list()
          processortype = list()
          for element in lines:
            #print(element)

            base_NamedElem_regex = re.compile(r'(.*)(base_NamedElement=")(.*?)(")')
            basenamemo = base_NamedElem_regex.search(element)
            if basenamemo is not None:
              baseName = basenamemo.group(3)
            
            base_execTime_regex = re.compile(r'(<execTime>)(\d+)')
            baseexecmo = base_execTime_regex.search(element)
            if baseexecmo is not None:
              baseexectime = baseexecmo.group(2)
              execTime.append(baseexectime)

            allocate_mem_regex = re.compile(r'(<allocatedMemory>)(\w+/*\w+\d*)')
            allocatememmo = allocate_mem_regex.search(element)
            if allocatememmo is not None:
              baseprocessortype = allocatememmo.group(2)
              processortype.append(baseprocessortype)

            for entries in topContainer:
              if baseName in entries.values():
                entries['value'] = execTime
                entries['type'] = processortype

    with open(input, "r") as infile:
      for lines in group_connector_lines(infile):
        cPorts = []
        if (lines[0].strip().startswith('<owned')):
          for element in lines:
            connector_name_regex = re.compile(r'(.*)(name=")(.*)(")')
            baseConnNamemo = connector_name_regex.search(element)
            if baseConnNamemo is not None:
              baseconnName = baseConnNamemo.group(3)
              cPorts.append(baseconnName)

            connector_role_regex = re.compile(r'(.*)(role=")(.*)(")')
            baseConnRolemo = connector_role_regex.search(element)
            if baseConnRolemo is not None:
              baseconnRole = baseConnRolemo.group(3)
              cPorts.append(baseconnRole)
              #print(baseconnRole)
          connectedPorts.append(cPorts)


    for entries in connectedPorts:
      for elements in topContainer:
        if entries[1] in elements['ports']:
          entries.append(elements['name'])
        if entries[2] in elements['ports']:
          entries.append(elements['name'])

    for entries in topContainer:
      if 'TopComponent' in entries.values():
        topContainer.remove(entries)

    print(connectedPorts)
    #print(topContainer)

    with open('t.csv', 'w') as task_out_f:
      csv_write = csv.writer(task_out_f)
      csv_write.writerow('t')
      for entries in topContainer:
        row = []
        if 'name' in entries.keys():
          row.append(entries['name'])
        csv_write.writerow(row)

    #with open('h.csv', 'w') as task_out_f:
      #csv_write = csv.writer(task_out_f)
      #csv_write.writerow('h')
      #for entries in topContainer:
        #row = []
        #if 'name' in entries.keys():
          #pe = ""
          #for elements in entries['type']:
            #if pe == "":
              #pe = elements
            #else:
              #pe = pe + ',' + elements
          #row.append(pe)
        #csv_write.writerow(row)
    with open('h.csv', 'w') as task_out_f:
      csv_write = csv.writer(task_out_f)
      csv_write.writerow('h')
      for entries in hwlistrows:
        row = []
        row.append(entries[0])
        csv_write.writerow(row)

    with open('connection.csv', 'w') as task_out_f:
      csv_write = csv.writer(task_out_f)
      for entries in connectedPorts:
        if len(entries) > 4:
          row = []
          row.append(entries[3])
          row.append(entries[4])
          csv_write.writerow(row)

    header_row = list()
    header_row_type = list()
    header_row.append('t')
    header_row_type.append('t')
    for entries in hwlistrows:
      header_row.append(entries[0])
      header_row_type.append(entries[-1])

    with open('Implementability.csv', 'w') as task_out_f:
      csv_write = csv.writer(task_out_f)
      csv_write.writerow(header_row)
      for entries in topContainer:
        row = []
        if 'name' in entries.keys():
          row.append(entries['name'])
        for elements in header_row_type[1:len(header_row_type)]:
          if elements in entries['type']:
            row.append(1)
          else:
            row.append(0)
        csv_write.writerow(row)

    with open('task_data.csv', 'w') as task_out_f:
      csv_write = csv.writer(task_out_f)
      csv_write.writerow(header_row)
      for entries in topContainer:
        row = []
        if 'name' in entries.keys():
          row.append(entries['name'])
        for elements in header_row_type[1:len(header_row_type)]:
          if elements in entries['type']:
            row.append(entries['value'][entries['type'].index(elements)])
            #if (len(entries['type']) == 1):
              #row.append(entries['value'])
            #else:
              #row.append(entries['value'][entries['type'].index(elements)])
          else:
            row.append(0)
        csv_write.writerow(row)
      

if __name__ == "__main__":
  main()
