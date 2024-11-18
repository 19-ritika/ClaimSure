def generate_email_report(claim_data):
    """
    Function to generate an email report for a claim.
    Takes claim_data as input and returns an email subject and body.

    :param claim_data: A dictionary containing claim details like ClaimTitle, ClaimType, ClaimDetails, SubmissionDate, and DueDate
    :return: A dictionary with email subject and body
    """
    # Extract necessary claim fields
    claim_title = claim_data.get('ClaimTitle', 'N/A')
    claim_type = claim_data.get('ClaimType', 'N/A')
    claim_details = claim_data.get('ClaimDetails', 'N/A')
    submission_date = claim_data.get('SubmissionDate', 'N/A')
    due_date = claim_data.get('DueDate', 'N/A')

    # Create the email body
    email_body = f"""
    Hello,

    Your claim has been submitted successfully. Below are the details of your claim:

    Claim Title: {claim_title}
    Claim Type: {claim_type}
    Claim Details: {claim_details}
    Submission Date: {submission_date}
    Due Date: {due_date}

    If you have any questions, please contact us.

    Best regards,
    Your Claims Team
    """

    # Create the email subject
    email_subject = f"Claim Submitted: {claim_title}"

    # Return the subject and body as a dictionary
    return {
        'subject': email_subject,
        'body': email_body
    }
