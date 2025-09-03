import argparse
import csv
import os
import textwrap

def create_rules(csv_file):
    rules = ""
    with open(csv_file) as f:
        reader = csv.DictReader(f)
        for row in reader:
            rule_entry = f"""\
      - IpProtocol: {row["Protocol"]}
        Description: {row["Description"]}
        FromPort: {row["FromPort"]}
        ToPort: {row["ToPort"]}
        CidrIp: {row["CidrIp"]}
"""
            rules += rule_entry
    
    return rules

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
    args=parser.parse_args()

    # If any of the args are missing, ask the user for the values
    for arg in args.__dict__:
        if args.__dict__[arg] is None:
            setattr(args, arg, input(f"Please enter the value for {arg}: "))
    
    # Set the Cloudformation header
    CFN_HEADER = textwrap.dedent(f"""\
                              AWSTemplateFormatVersion: 2010-09-09

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

    sg_rules = create_rules('example.csv')
    resources_block += sg_rules
    template = CFN_HEADER + resources_block + CFN_FOOTER
    with open(working_directory + args.service_name + "SecurityGroup.template.yaml", "w") as f:
        f.write(template)
    
    print(f"\nTemplate generated as {args.service_name}SecurityGroup.template.yaml. Exiting.")