import os
import subprocess
import boto3
import time

# Configuration
AWS_REGION = "us-west-2"
KEY_NAME = "your-key-name"
SECURITY_GROUP_NAME = "automation_sg"
INSTANCE_TYPE = "t2.micro"
AMI_ID = "ami-0c55b159cbfafe1f0"  # Replace with a valid AMI ID for your region

# AWS Client
ec2_client = boto3.client('ec2', region_name=AWS_REGION)

def create_key_pair():
    key_pair = ec2_client.create_key_pair(KeyName=KEY_NAME)
    private_key = key_pair['KeyMaterial']
    with open(f"{KEY_NAME}.pem", "w") as file:
        file.write(private_key)
    os.chmod(f"{KEY_NAME}.pem", 0o400)
    print(f"Created key pair: {KEY_NAME}")
    
def create_security_group():
    response = ec2_client.create_security_group(GroupName=SECURITY_GROUP_NAME, Description="Security group for automation script")
    security_group_id = response['GroupId']
    ec2_client.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=[
            {'IpProtocol': 'tcp', 'FromPort': 22, 'ToPort': 22, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp', 'FromPort': 80, 'ToPort': 80, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp', 'FromPort': 8080, 'ToPort': 8080, 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
        ]
    )
    print(f"Created security group: {SECURITY_GROUP_NAME} with ID: {security_group_id}")
    return security_group_id

def create_instance(security_group_id, instance_name):
    instance = ec2_client.run_instances(
        ImageId=AMI_ID,
        InstanceType=INSTANCE_TYPE,
        KeyName=KEY_NAME,
        MinCount=1,
        MaxCount=1,
        SecurityGroupIds=[security_group_id],
        TagSpecifications=[{'ResourceType': 'instance', 'Tags': [{'Key': 'Name', 'Value': instance_name}]}]
    )
    instance_id = instance['Instances'][0]['InstanceId']
    print(f"Created instance {instance_name} with ID: {instance_id}")
    return instance_id

def get_instance_public_ip(instance_id):
    while True:
        response = ec2_client.describe_instances(InstanceIds=[instance_id])
        public_ip = response['Reservations'][0]['Instances'][0].get('PublicIpAddress')
        if public_ip:
            print(f"Instance {instance_id} public IP: {public_ip}")
            return public_ip
        time.sleep(5)

def run_ansible_playbook(inventory_content):
    with open("ansible/inventory", "w") as file:
        file.write(inventory_content)
    
    subprocess.run(["ansible-playbook", "-i", "ansible/inventory", "ansible/playbook.yml"], check=True)
    print("Ansible playbook executed successfully")

def main():
    create_key_pair()
    security_group_id = create_security_group()
    
    app_instance_id = create_instance(security_group_id, "AppInstance")
    jenkins_instance_id = create_instance(security_group_id, "JenkinsInstance")
    
    app_instance_ip = get_instance_public_ip(app_instance_id)
    jenkins_instance_ip = get_instance_public_ip(jenkins_instance_id)
    
    inventory_content = f"""[web]
{app_instance_ip} ansible_user=ec2-user ansible_private_key_file=~/.ssh/{KEY_NAME}.pem

[jenkins]
{jenkins_instance_ip} ansible_user=ec2-user ansible_private_key_file=~/.ssh/{KEY_NAME}.pem
"""
    
    run_ansible_playbook(inventory_content)

if __name__ == "__main__":
    main()
