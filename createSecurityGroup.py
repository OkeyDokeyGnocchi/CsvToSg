import argparse
import csv
import ipaddress
import os
import re
import textwrap

def create_rules(csv_file):
    # Create our rules for the CFN template by looping through our input csv file
    cfn_rules = ""
    header_parameters = ""
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Check if the row's CidrIp column contains letters
            # This would generally mean that this will be a parameter for human-readability
            if re.search('[a-zA-Z]', row["CidrIp"]):
                cidr_format = False
                while cidr_format == False:
                  # If this appears to be a non-CIDR, ask user for the CIDR so we can set the parameter
                  param_cidr = input(f"What is the CIDR IP for {row['CidrIp']}: ")
                  if not validate_cidr(param_cidr):
                      print("IP range MUST be in CIDR format. e.g., 129.65.0.0/16\n")
                  else:
                    # If non-CIDR we need to create the parameter(s) up in the header
                    header_parameters += f"""\
  {row['CidrIp']}:
    Type: String
    Default: {param_cidr}
"""
                    rule_entry = f"""\
        - IpProtocol: {row["Protocol"]}
          Description: \"{row["Description"]}\"
          FromPort: {row["StartingPort"]}
          ToPort: {row["EndingPort"]}
          CidrIp: !Ref {row["CidrIp"]}
"""
                    break
            else:
                rule_entry = f"""\
        - IpProtocol: {row["Protocol"]}
          Description: \"{row["Description"]}\"
          FromPort: {row["StartingPort"]}
          ToPort: {row["EndingPort"]}
          CidrIp: {row["CidrIp"]}
"""
            cfn_rules += rule_entry
    
    return cfn_rules, header_parameters

def validate_cidr(cidr_input):
    try:
        ipaddress.ip_network(cidr_input)
        return True
    except:
        return False

if __name__ == '__main__':

    working_directory = os.path.dirname(os.path.abspath(__file__)) + "/"

    print()

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
    
    TAGS_FILE = textwrap.dedent(f"""\
                                Tags:
                                - Key: BillFund
                                  Value: <ChangeMe>
                                - Key: BillDeptId
                                  Value: <ChangeMe>
                                - Key: BillAccount
                                  Value: <ChangeMe>
                                - Key: PrimaryContact
                                  Value: <ChangeMe>
                                - Key: DataClassification
                                  Value: <ChangeMe>
                                - Key: ServiceName
                                  Value: {args.service_name}
                                - Key: ServiceComponent
                                  Value: <ChangeMe>""")

    sg_rules = create_rules(args.csv_file)

    # Add our generated rules to the resources block and parameters to the header
    resources_block += sg_rules[0]
    CFN_HEADER += sg_rules[1]

    # Build our template
    template = CFN_HEADER + "\n" + resources_block + CFN_FOOTER

    # Save the template
    with open(working_directory + args.service_name + "SecurityGroup.template.yaml", "w") as f:
        f.write(template)

    # Save the tags file
    with open(working_directory + args.service_name + "SecurityGroup.tags.yaml", "w") as f:
        f.write(TAGS_FILE)
    
    print(f"\nTemplate generated as {args.service_name}SecurityGroup.template.yaml.")
    print(f"Tags file generated as {args.service_name}SecurityGroup.tags.yaml.")
    print(f"\n##NOTE: Please be sure to put the correct values in for the tags before uploading! Exiting.")