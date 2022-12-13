import datetime
import re
import smtplib
from os.path import basename
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formatdate


def run(all_analytics, all_changes):
    changes = all_changes[0]
    new_mappings = all_changes[1]
    location_duplicates = all_changes[2]
    non_mapped_locations = all_changes[3]
    error_locations = all_changes[4]

    now = datetime.datetime.now()
    date = str(now)
    date = re.sub(":", "-", date)
    date = re.sub("\.[0-9]+", "", date)

    name = f"Close to ST Analytics Report for {date}"

    f = open(f"{name}.txt", "w")

    f.write("ANALYTICS REPORT\n"
            f"Date: {now.date()}\n"
            f"Time: {now.time()}\n"
            f"\n"
            f"Total Entries Checked on Close: {len(all_analytics)}\n"
            f"Entries Checked:")

    for array in all_analytics:
        f.write(f"\n\t - {array}")

    f.write(
        f"\n\nTotal Entries Changes on Close: {len(changes)}\n"
        f"Entries Changed:"
    )

    for array in changes:
        f.write(f"\n\t - {array}")

    f.write("\n\nNew Close Mappings:")
    for array in new_mappings:
        if array:
            for new_mapping in array:
                f.write(f"\n\t - {', '.join(new_mapping)}")

    f.write("\n\nLocation Duplicates:")
    true_duplicates = []
    for location_duplicate in location_duplicates:
        for array in location_duplicate:
            if array not in true_duplicates:
                true_duplicates.append(array)

    for dupe in true_duplicates:
        f.write(f"\n\t - {dupe}")

    f.write("\n\nNon-Mapped Locations:")
    for array in non_mapped_locations:
        if array:
            f.write(f"\n\t - {array}")

    f.write("\n\nError Locations:")
    for error_location in error_locations:
        if error_location:
            for array in error_location:
                f.write(f"\n\t - {', '.join(array)}")

    f.write(f"\n\nNote: Contacts are not being checked because stuff is being dumb")

    f.close()

    '''send_mail(
        "ajrb@albertaindoorcomfort.com",
        "ajrberezowski@gmail.com",
        "Testing File Sending",
        "Test",
        [f"{name}.txt"]
    )'''


def send_mail(send_from, send_to, subject, text, files=None, server="127.0.0.1"):

    msg = MIMEMultipart()
    msg['From'] = send_from  # From email
    msg['To'] = send_to  # To email
    msg['Date'] = formatdate(localtime=True)
    msg['Subject'] = subject  # Subject line

    msg.attach(MIMEText(text))

    for f in files or []:
        print(f"\t\t\tFile: {f} of {files}")
        with open(f, "rb") as fil:
            part = MIMEApplication(
                fil.read(),
                Name=basename(f)
            )
        # After the file is closed
        part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
        msg.attach(part)

    smtp = smtplib.SMTP(server)
    smtp.sendmail(send_from, send_to, msg.as_string())
    smtp.close()
