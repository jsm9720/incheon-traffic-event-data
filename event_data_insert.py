'''
작성일 : 2020. 12. 23.
작성자 : 정성모
코드 개요 : event_data를 전처리하여 accumulo에 삽입
            - 원 데이터 : 접수번호,접수일,시간,방송시간,전송,중요,방송,DLS,제보유형,제보자,TYPE,제보처,접수자,내용
            - Key : rowID : 접수일+시간+접수번호, cq : 제보유형
            - Value : 방송시간,전송,중요,방송DLS,제보자,TYPE,제보처,접수자,내용,GPS포인트(1~N)
'''
import pandas as pd
import numpy as np
import pysharkbite
import math

def main():

    read_file = 'result/%s.xlsx' % 9
    data = pd.read_excel(read_file,engine='openpyxl',header=0, index_col=0)
    data.dropna(how='all', axis='columns', inplace = True)
    data = data[~data['GPS포인트1'].isnull()]
    # print(data[data['GPS포인트1'] == 0]) 0도 필터링 됬는지 확인
    data_list = data.values.astype(str).tolist()
    print(len(data_list))
    for i in range(len(data_list)):
        if not 'nan' in data_list[i]:
            continue
        data_list[i] = data_list[i][:data_list[i].index('nan')]
        break

    #action_accumulo(data_list)
    

def action_accumulo(rows):
    '''
    함수개요 : accumulo insert or query 
    매개변수 : rows = 삽입할 데이터(type:list)
    '''
    try:
        zoo_instance = "dblab"
        zookeepers = "dblab-node-01:2182,dblab-server-01:2182,dblab-server-02:2182,dblab-server-03:2182"
        username = "root"
        password = "1" 
        
        configuration = pysharkbite.Configuration()
        
        zk = pysharkbite.ZookeeperInstance(zoo_instance, zookeepers, 1000, configuration)
        
        user = pysharkbite.AuthInfo(username, password, zk.getInstanceId())

        connector = pysharkbite.AccumuloConnector(user, zk) 
        table_operations = connector.tableOps("Event_Data")
        auths = pysharkbite.Authorizations()
        
        # Accumulo Write
        writer = table_operations.createWriter(auths, 10)
        count = 0
        for row in rows:
            key = '%s %s %s' % (row[1],row[2],row[0])
            cq = row[8]
            row.remove(row[8])
            val = str(row[3:])[1:-1].replace("\'","")

            mutation = pysharkbite.Mutation(key)
            mutation.put("",cq,"", 0,val)
            writer.addMutation(mutation)
            count += 1
            if count % 1000 == 0:
                print(count)
        writer.close()

        # Accumulo Read
        # scanner = table_operations.createScanner(auths, 2)

        # range = pysharkbite.Range("2020-01-01 06:53 202001467140")
        # scanner.addRange(range)
        # resultset = scanner.getResultSet()

        # for keyvalue in resultset:
        #     key = keyvalue.getKey()
        #     assert("2020-01-01 06:53 202001467140" == key.getRow())
        #     value = keyvalue.getValue()
        #     print()
        #     print("Key :",key)
        #     print("Value :",value)
        #     print()

    except Exception as e:
        print("disconnect")
        print(e)
    return 0



main()
 
