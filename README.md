## Simple python script to create a CloudFormation template for Security Groups from a csv
- If column for `CidrIp` contains letters, it is assumed that you would like a named parameter to reference a Cidr
- - e.g., "Vlan123" will cause script to prompt for the Cidr for the Vlan and will create and !Ref a parameter

### Csv example
```
Action,Direction,StartingPort,EndingPort,Protocol,CidrIp,DisplayName,Description
Allow,Inbound,80,80,tcp,129.65.0.0/16,Rule1,I am the first rule
Allow,Inbound,443,443,tcp,129.65.0.0/16,Rule2,I am the second rule
Allow,Inbound,27000,27009,tcp,10.149.0.0/22,Rule3,I am the third rule
Allow,Inbound,27000,27009,tcp,129.65.10.0/24,Rule4,I am the fourth rule
Allow,Inbound,27000,27009,tcp,129.65.0.0/16,OnPremFlexAccess,Allow campus to access FlexNet Ports
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