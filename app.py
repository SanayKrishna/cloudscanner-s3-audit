from flask import Flask, render_template, jsonify
from utils.s3_scanner import scan_s3_buckets
from datetime import datetime
import boto3
from botocore.exceptions import ClientError

app = Flask(__name__)

@app.route('/')
def dashboard():
    return render_template('dashboard.html')

@app.route('/scan')
def scan():
    """API endpoint for AJAX refresh - re-runs S3 scanner"""
    try:
        print("🔍 Starting S3 bucket scan...")
        
        # Re-run the S3 scanner
        results = scan_s3_buckets()

        public_buckets = results.get('public_buckets', [])
        versioning_disabled = results.get('versioning_disabled', [])
        unencrypted_buckets = results.get('unencrypted_buckets', [])

        # Total buckets scanned (unique)
        all_buckets = set(public_buckets + versioning_disabled + unencrypted_buckets)
        total_buckets = len(all_buckets)

        print(f"✅ Scan complete - Found {len(public_buckets)} public, {len(versioning_disabled)} unversioned, {len(unencrypted_buckets)} unencrypted")

        return jsonify({
            'success': True,
            'data': {
                'public_buckets': public_buckets,
                'versioning_disabled': versioning_disabled,
                'unencrypted_buckets': unencrypted_buckets,
                'public_count': len(public_buckets),
                'versioning_count': len(versioning_disabled),
                'unencrypted_count': len(unencrypted_buckets),
                'total_buckets': total_buckets,
                'generated_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        })
    except Exception as e:
        print(f"❌ Scan failed: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/bucket-details/<bucket_name>')
def bucket_details(bucket_name):
    """Get detailed information about a specific bucket"""
    try:
        print(f"📊 Fetching details for bucket: {bucket_name}")
        s3_client = boto3.client('s3')
        
        details = {
            'bucket_name': bucket_name,
            'objects': [],
            'versioning_status': 'Unknown',
            'encryption_status': 'Unknown',
            'public_access_block': {},
            'total_objects': 0,
            'total_size': 0
        }

        # Get versioning status
        try:
            versioning = s3_client.get_bucket_versioning(Bucket=bucket_name)
            details['versioning_status'] = versioning.get('Status', 'Disabled')
        except ClientError as e:
            print(f"⚠️ Could not get versioning: {e}")

        # Get encryption status
        try:
            encryption = s3_client.get_bucket_encryption(Bucket=bucket_name)
            rules = encryption.get('ServerSideEncryptionConfiguration', {}).get('Rules', [])
            if rules:
                details['encryption_status'] = rules[0].get('ApplyServerSideEncryptionByDefault', {}).get('SSEAlgorithm', 'Unknown')
            else:
                details['encryption_status'] = 'None'
        except ClientError as e:
            if e.response['Error']['Code'] == 'ServerSideEncryptionConfigurationNotFoundError':
                details['encryption_status'] = 'None'
            else:
                print(f"⚠️ Could not get encryption: {e}")

        # Get public access block configuration
        try:
            public_block = s3_client.get_public_access_block(Bucket=bucket_name)
            config = public_block.get('PublicAccessBlockConfiguration', {})
            details['public_access_block'] = {
                'block_public_acls': config.get('BlockPublicAcls', False),
                'ignore_public_acls': config.get('IgnorePublicAcls', False),
                'block_public_policy': config.get('BlockPublicPolicy', False),
                'restrict_public_buckets': config.get('RestrictPublicBuckets', False)
            }
        except ClientError as e:
            if e.response['Error']['Code'] == 'NoSuchPublicAccessBlockConfiguration':
                details['public_access_block'] = {
                    'block_public_acls': False,
                    'ignore_public_acls': False,
                    'block_public_policy': False,
                    'restrict_public_buckets': False
                }

        # List objects (first 100)
        try:
            response = s3_client.list_objects_v2(Bucket=bucket_name, MaxKeys=100)
            
            if 'Contents' in response:
                details['total_objects'] = response.get('KeyCount', 0)
                
                for obj in response['Contents']:
                    # Get object ACL to check if public
                    is_public = False
                    try:
                        acl = s3_client.get_object_acl(Bucket=bucket_name, Key=obj['Key'])
                        for grant in acl.get('Grants', []):
                            grantee = grant.get('Grantee', {})
                            if grantee.get('Type') == 'Group' and 'AllUsers' in grantee.get('URI', ''):
                                is_public = True
                                break
                    except:
                        pass

                    # Get object encryption
                    obj_encryption = 'None'
                    try:
                        head = s3_client.head_object(Bucket=bucket_name, Key=obj['Key'])
                        obj_encryption = head.get('ServerSideEncryption', 'None')
                    except:
                        pass

                    details['objects'].append({
                        'key': obj['Key'],
                        'size': obj['Size'],
                        'last_modified': obj['LastModified'].strftime("%Y-%m-%d %H:%M:%S"),
                        'storage_class': obj.get('StorageClass', 'STANDARD'),
                        'is_public': is_public,
                        'encryption': obj_encryption
                    })
                    details['total_size'] += obj['Size']

                # Check if there are more objects
                if response.get('IsTruncated', False):
                    details['has_more'] = True
            else:
                details['total_objects'] = 0

        except ClientError as e:
            print(f"⚠️ Could not list objects: {e}")
            details['error'] = str(e)

        print(f"✅ Retrieved details for {bucket_name}: {details['total_objects']} objects")
        
        return jsonify({
            'success': True,
            'data': details
        })

    except Exception as e:
        print(f"❌ Error getting bucket details: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(debug=True)