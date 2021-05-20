def request_seen(self, request):
    fp = request_fingerprint(request)
    if self.bf.isContains(fp):    # 如果已经存在
        return True
    else:
        self.bf.insert(fp)
        return False