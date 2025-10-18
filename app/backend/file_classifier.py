def getFileType(file_name):
    if (isCode(file_name)):
        return "code"
    elif (isText(file_name)):
        return "text"
    else:
        return "other"