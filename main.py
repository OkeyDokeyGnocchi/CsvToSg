import argparse
import csv
import os
import re
import textwrap

def create_rules(csv_file, CFN_HEADER):
    # Create our rules for the CFN template by looping through our input csv file
    cfn_rules = ""
    header_parameters = ""
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            if re.search('[a-zA-Z]', row["CidrIp"]):
                cidr_format = False
                while cidr_format == False:
                  param_cidr = input(f"What is the CIDR IP for {row['CidrIp']}: ")
                  if not re.search('([0-9]{1,3}\.){3}[0-9]{1,3}(\\[0-3][0-9])', param_cidr):
                      print("IP range MUST be in CIDR format. e.g., 129.65.0.0/16")
                  else:
                    header_parameters += f"""\
  {row['CidrIp']}:
      Type: String
      Default: {param_cidr}
"""
            else:
                rule_entry = f"""\
      - IpProtocol: {row["Protocol"]}
        Description: \"{row["Description"]}\"
        FromPort: {row["FromPort"]}
        ToPort: {row["ToPort"]}
        CidrIp: {row["CidrIp"]}
"""
            cfn_rules += rule_entry
    
    return cfn_rules, header_parameters

if __name__ == '__main__':

    working_directory = os.path.dirname(os.path.abspath(__file__)) + "/"

    # Set up the argument parser
    parser = argparse.ArgumentParser()

    # Add our command line arguments to the parser
    parser.add_argument("--service-name", help="Service name")
    parser.add_argument("--deploy-doc", help = "URL for the deploy doc")
    parser.add_argument("--repo-name", help = "Name of the code repository")
    parser.add_argument("--repo-url", help = "URL for the code repository")
    parser.add_argument("--repo-account", help = "AWS account that the repository is in")
    parser.add_argument("--csv-file", help="The input csv file to generate rules from")
    args=parser.parse_args()

    # If any of the args are missing, ask the user for the values
    for arg in args.__dict__:
        if args.__dict__[arg] is None:
            setattr(args, arg, input(f"Please enter the value for {arg}: "))
    
    # Set the Cloudformation header
    CFN_HEADER = textwrap.dedent(f"""\
                              AWSTemplateFormatVersion: \"2010-09-09\"

                              Parameters:
                                GroupName:
                                  Type: String
                                  Default: \"{args.service_name}\"
                                  """)

    # Set the Resources block starter
    resources_block = textwrap.dedent(f"""\
                                      Resources:
                                        {args.service_name}SG:
                                          Type: AWS::EC2::SecurityGroup
                                          Properties:
                                            GroupDescription: {args.service_name} Security Group
                                            GroupName: !Ref GroupName
                                            VpcId: !ImportValue Network-ItsVpc::VPC
                                            SecurityGroupIngress:
                                      """)

    # Set the Cloudformation , incl. the Tags section
    CFN_FOOTER = textwrap.dedent(f"""\
                                      Tags:
                                        - {{ Key: Name, Value: !Ref GroupName }}
                                 
                                Outputs:
                                  DeployDoc:
                                    Description: URL of the stack's deployment doc
                                    Value: {args.deploy_doc}
                                  RepoName:
                                    Description: Name of the repo containing the stack's code
                                    Value: {args.repo_name}
                                  RepoCloneUrl:
                                    Description: Clone URL of the repo containig the stack's code
                                    Value: {args.repo_url}
                                  RepoAcct:
                                    Description: Alias of the AWS account containing the repo
                                    Value: {args.repo_account}""")

    sg_rules = create_rules(args.csv_file, CFN_HEADER)
    resources_block += sg_rules[0]
    CFN_HEADER += sg_rules[1]
    template = CFN_HEADER + "\n" + resources_block + CFN_FOOTER
    with open(working_directory + args.service_name + "SecurityGroup.template.yaml", "w") as f:
        f.write(template)
    
    print(f"\nTemplate generated as {args.service_name}SecurityGroup.template.yaml. Exiting.")