import boto3
from botocore.exceptions import ClientError

ACCESS_KEY="YOUR_ACCESS_KEY"
SECRET_KEY="YOUR_SECRET_KEY"

VpcName='TEST-VPC'
VpcCidrBlock='10.10.0.0/16'
SubnetCidrBlock=['10.10.1.0/24','10.10.2.0/24']

ec2 = boto3.resource(
	'ec2',
	aws_access_key_id=ACCESS_KEY,
	aws_secret_access_key=SECRET_KEY
)

#Create VPC
try:
	vpc = ec2.create_vpc(CidrBlock=VpcCidrBlock)

	#Assign a name to our VPC
	vpc.create_tags(Tags=[{
		"Key": "Name", 
		"Value": VpcName
	}])
	vpc.wait_until_available()
	print("1.Create and Assign a name to VPC successfully.")
	
	#Enable DNS Support and DNSHostname Support
	ec2Client = boto3.client('ec2')
	ec2Client.modify_vpc_attribute( 
		VpcId = vpc.id , 
		EnableDnsSupport = { 
			'Value': True 
		} 
	)
	ec2Client.modify_vpc_attribute( 
		VpcId = vpc.id , 
		EnableDnsHostnames = { 
			'Value': True 
		}  
	)
	print("2.Enable DNS support successfully.")

	# Create an internet gateway and attach it to VPC
	internetgateway = ec2.create_internet_gateway()
	vpc.attach_internet_gateway(
		InternetGatewayId=internetgateway.id
	)
	print("3.Create Internet Gateway successfully.")

	# Create a route table and a public route
	routetable = vpc.create_route_table()
	route = routetable.create_route(
		DestinationCidrBlock='0.0.0.0/0', 
		GatewayId=internetgateway.id
	)
	print("4.Create Routing table successfully.")

	# Create subnet and associate it with route table
	for i in range(len(SubnetCidrBlock)):
		if(i==0):
			azId = 'a'
		else:
			azId = 'b'
		subnetName = "SUBNET-" + azId.upper()
		azName = 'ap-southeast-1' + azId
		subnet = ec2.create_subnet(
			AvailabilityZone=azName,
			CidrBlock=SubnetCidrBlock[i], 
			VpcId=vpc.id
		)
		addSubnetName = ec2.create_tags(
    		Resources=[
        		subnet.id,
    		],
    		Tags=[
        		{
            		'Key': 'Name',
            		'Value': subnetName
        		},
    		]
		)
		routetable.associate_with_subnet(SubnetId=subnet.id)
	print("5.Create Subnet successfully.")

except ClientError as e:
	print("ERROR !!! ")
	print(e)
