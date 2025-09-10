## Simple python script to create a CloudFormation template for Security Groups from a csv
- If column for `CidrIp` contains letters, it is assumed that you would like a named parameter to reference a Cidr
- - e.g., "Vlan123" will cause script to prompt for the Cidr for the Vlan and will create and !Ref a parameter

### Csv example
```
DisplayName,Description,Action,Direction,FromPort,ToPort,Protocol,CidrIp
Rule1,I am the first rule,Allow,Inbound,80,80,tcp,129.65.0.0/16
Rule2,I am the second rule,Allow,Inbound,27000,27009,tcp,129.65.0.0/16
```

### Example CLI run
```
python createSecurityGroup.py \
--csv-file myCsv.csv \
--service-name MyService \
--deploy-doc https://wiki.wiki \
--repo-name RepoName \
--repo-url htts://codecommit.code \
--repo-account cptest-dev
```