#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
import os
import json
import shutil
import os.path as path
from glob2 import glob
from variant import is_variant

try:
    from cdifflib import CSequenceMatcher
except ImportError:
    # Windows上跳过安装cdifflib
    def CSequenceMatcher(isjunk, a, b, autojunk):
        return [isjunk, a, b, autojunk] and []


class GlTool(object):
    """ 高丽藏处理函数"""
    DATA_DIR = '/Users/xiandu/Document/03Work/藏经数字化/校对项目/高丽藏'  # gl-data所在目录

    def __init__(self):
        self.qzw = None  # 千字文
        self.vt_dict1 = None  # 异体字字典1
        self.vt_dict2 = None  # 异体字字典2
        self.char2unicode = None  # 自造字转unicode

    def load_qzw(self):
        """ 加载千字文"""
        with open('./assets/qzw.txt', 'r') as fn:
            lines = [ln.strip() for ln in fn.readlines()]
            self.qzw = ''.join(lines)

    def load_variant_dict(self):
        """高丽藏异体字字典"""
        with open('./assets/variants1.json', 'r') as rf:
            self.vt_dict1 = json.load(rf)
        with open('./assets/variants2.json', 'r') as rf:
            self.vt_dict2 = json.load(rf)

    def load_char2unicode(self):
        """ Text中的自造字的Unicode对应表"""
        char2unicode = dict()
        with open('./assets/SelfChar2Unicode.txt', 'r') as fn:
            lines = fn.readlines()
            for ln in lines[1:]:
                ch1, ch2 = ln.strip().split('\t')
                char2unicode[ch1] = ch2
        self.char2unicode = char2unicode

    def trans_char2unicode(self, txt):
        """ 替换高丽藏的自造字"""
        ret = ''
        for t in txt:
            ret += self.char2unicode.get(t) or t
        return ret

    @classmethod
    def get_file_num(cls, folder='DocxStdTxt'):
        files = glob(path.join(GlTool.DATA_DIR, folder, '**', '*.txt'))
        return len(files)

    @staticmethod
    def trim_wan(txt):
        txt = re.sub(r'(^[卍卐]+)([^\d字音者相下]|$)', r'\2', txt)  # 去掉行首连续的万字符
        txt = re.sub(r'(^\d\d:)([卍卐]+)', r'\1', txt)  # 去掉行首连续的万字符
        txt = re.sub(r'(^|[^聲作下])([卍卐]+$)', r'\1', txt)  # 去掉行尾连续的万字符
        return txt

    @classmethod
    def get_lines(cls, name, folder='DocxStdTxt'):
        name = name.rstrip('.txt')
        src_file = path.join(cls.DATA_DIR, folder, name.split('_')[1], name + '.txt')
        if path.exists(src_file):
            with open(src_file, 'r') as rf:
                return rf.readlines()

    @classmethod
    def write_lines(cls, name, lines, folder):
        name = name.rstrip('.txt')
        dst_dir = path.join(cls.DATA_DIR, folder, name.split('_')[1])
        not path.exists(dst_dir) and os.makedirs(dst_dir)
        with open(path.join(dst_dir, name + '.txt'), 'w') as wf:
            wf.writelines(lines)

    @classmethod
    def copy_files(cls, src_folder, dst_folder):
        src_dir = path.join(cls.DATA_DIR, src_folder)
        for root, dirs, files in os.walk(src_dir):
            for fn in files:
                name, ext = fn.rsplit('.', 1)
                if ext != 'txt':
                    continue
                dst_dir = path.join(cls.DATA_DIR, dst_folder, fn.split('_')[1])
                not path.exists(dst_dir) and os.makedirs(dst_dir)
                shutil.copy(path.join(root, fn), path.join(dst_dir, fn))

    @classmethod
    def print_files(cls, names, folder='DocxOriTxt'):
        for name in names:
            print('-------------%s-------------' % name)
            lines = cls.get_lines(name, folder) or []
            for ln in lines:
                print(ln.rstrip())

    @classmethod
    def cmp_file(cls, fn, folder1='DocxOriTxt', folder2='DocxStdTxt', folder3='Text2Page'):
        print('----------%s vs %s vs %s----------' % (folder1, folder2, folder3))
        lines1 = folder1 and cls.get_lines(fn, folder1) or []
        lines2 = folder2 and cls.get_lines(fn, folder2) or []
        lines3 = folder3 and cls.get_lines(fn, folder3) or []
        length = max(len(lines1), len(lines2), len(lines3))
        for i in range(length):
            msg = ''
            if folder1 and i < len(lines1):
                msg += ' [1]' + lines1[i].rstrip('\n')
            if folder2 and i < len(lines2):
                msg += ' [2]' + lines2[i].rstrip('\n')
            if folder3 and i < len(lines3):
                msg += ' [3]' + lines3[i].rstrip('\n')
            print(msg)

    @classmethod
    def find_txt(cls, txt, folder, encoding='utf-8', cnt=1, existed=True, names=None):
        src_path = path.join(cls.DATA_DIR, folder)
        for root, dirs, files in os.walk(src_path):
            for fn in files:
                name, ext = fn.rsplit('.', 1)
                if ext != 'txt' or (names and name not in names):
                    continue
                with open(path.join(root, fn), 'r', encoding=encoding) as rf:
                    content = ''.join(rf.readlines()).replace('\n', '')
                sh = re.search('(<.*>).*(<.*>)', content)
                if sh:
                    print('[%s#%s]%s' % (fn, cnt, '%s...%s' % (sh.group(1), sh.group(2))))
                    cnt -= 1
                    if cnt < 1:
                        return
                # idx = content.find(txt)
                # # existed表示查询存在或者不存在某字
                # if (existed and idx > -1) or (not existed and idx == -1):
                #     s = 0 if idx < 10 else idx - 10
                #     print('[%s#%s]%s' % (fn, cnt, content[s:idx + 10]))
                #     cnt -= 1
                #     if cnt < 1:
                #         return

    def oritxt0_2_oritxt(self, fn):
        valid = True
        lines, lno = [], 1
        with open(fn, 'r') as rf:
            for ln in rf.readlines():
                ln = re.sub(r'\s+', '', ln)
                fname = fn.rsplit('/', 1)[1]
                mt = re.match(r'^K\d+V\d+P\d+[Labcdef]\s?(\d+)L?;(.*)$', ln)
                if not mt:
                    valid = False
                    print('[e1]%s: %s' % (fname, ln))
                    continue
                # 清洗文本
                no, txt0 = mt.groups()
                txt = self.trans_char2unicode(txt0)  # 0.替换自造字
                txt = re.sub(r'\*\d', '', txt)  # 1.去掉“星号+数字”组合
                txt = re.sub(r'[+#ㅜㅡㅋ◦ㅍ◑ㅁ,;*\'`\-\]\(\)\/A-Za-z]+', '', txt)  # 2.去掉特殊字符
                txt = re.sub(r'(\d)\d+', r'\1', txt)  # 3.连续数字仅保留第一位
                txt = re.sub(r'^\d+', '', txt)  # 4.去掉起首的连续数字
                txt = re.sub(r'\s+', '', txt)  # 5.去掉空白
                txt = self.trim_wan(txt)  # 6.去掉万字符
                # 格式匹配
                fh = '&'  # 特殊符号
                fw = '𑖡𑖦𑖾𑖭𑖦𑖽𑖝𑖪𑖟𑖿𑖨𑖧𑖪𑖺𑖠𑖰𑖭𑖝𑖿𑖪𑖯𑖧𑖦𑖮𑖯𑖭𑖝𑖿𑖪𑖯𑖧𑖭𑖮𑖯𑖎𑖯𑖨𑗜𑖜𑖰𑖎𑖯𑖧𑖝𑖟𑖿𑖧𑖞𑖯𑖌𑖼𑖪𑖨𑖘𑖰𑖪𑖨𑖘𑖰𑖪𑖨𑖪𑖨𑖝𑖰𑖭𑖯𑖮𑖯'  # 梵文
                mt3 = re.match(r'^[\u3400-\uFAD9\U00020000-\U0003134A\d〇%s%s]+$' % (fh, fw), txt)
                if txt and not mt3:
                    valid = False
                    print('[e2]%s: %s' % (fname, ln))
                    continue
                # 字体编号转换
                txt = txt.replace('3', '1').replace('4', '2')
                txt = txt.replace('5', '').replace('6', '').replace('7', '')
                if txt:
                    lines.append('%02d:%s\n' % (lno, txt))
                    lno += 1
        return lines, valid

    def proc_oritxt0_to_oritxt(self, names=None):
        """ 将JL处理的DocxOriTxt0批量转为DocxOriTxt"""
        self.load_char2unicode()
        src_dir = path.join(self.DATA_DIR, 'DocxOriTxt0')
        for root, dirs, files in os.walk(src_dir):
            for fn in files:
                name, ext = fn.rsplit('.', 1)
                if ext != 'txt' or (names and name not in names):
                    continue
                lines, valid = self.oritxt0_2_oritxt(path.join(root, fn))
                valid and self.write_lines(name, lines, 'DocxOriTxt')

    def oritxt_to_stdtxt(self, txt, fn=None, err_cnt=None):
        """ 根据将高丽藏异体字字典，将原字文本转换为正字文本"""
        if not txt:
            return ''
        chars = []
        err_cnt = err_cnt or dict()
        for i, c in enumerate(txt):
            if c in '0123456789':
                if not chars:
                    print('[e1]%s: %s@%s,%s' % (fn, c, i + 1, txt.strip()))  # 首字为数字
                    continue
                trans = self.vt_dict1 if c == '1' else self.vt_dict2 if c == '2' else None
                if not trans:
                    print('[e2]%s: %s@%s,%s' % (fn, c, i + 1, txt.strip()))  # 异体字类型有误
                    continue
                if chars[-1] not in trans:
                    print('[e3]%s: %s@%s,%s' % (fn, c, i + 1, txt.strip()))  # 异体字字典无该字
                    key = chars[-1] + c
                    err_cnt[key] = err_cnt.get(key, 0) + 1
                    continue
                chars[-1] = trans.get(chars[-1])
            else:
                chars.append(c)
        return ''.join(chars), err_cnt

    def proc_oritxt_to_stdtxt(self, names=None):
        err_cnt = dict()
        self.load_variant_dict()
        self.load_char2unicode()
        src_dir = path.join(self.DATA_DIR, 'DocxOriTxt')
        for root, dirs, files in os.walk(src_dir):
            for fn in files:
                name, ext = fn.rsplit('.', 1)
                if ext != 'txt' or (names and name not in names):
                    continue
                with open(path.join(root, fn), 'r') as rf:
                    lines = []
                    for ln in rf.readlines():
                        no, oritxt = ln.split(':', 2)
                        nor_txt = self.oritxt_to_stdtxt(oritxt, fn, err_cnt)[0]
                        nor_txt = self.trans_char2unicode(nor_txt)
                        lines.append('%s:%s' % (no, nor_txt))
                    self.write_lines(name, lines, 'DocxStdTxt')
        for err, cnt in err_cnt.items():
            print(err, cnt)

    def proc_text2page0_to_text2page(self, names=None, display=1, err_cnt=100):
        """ 根据从DocxStdTxt，检查、完善Text2Page0得到text2page"""

        def get_list(lst, i):
            if 0 <= i < len(lst):
                return lst[i]
            return ''

        def set_list(lst, i, v):
            if 0 <= i < len(lst):
                lst[i] = v

        def get_txt(t1):
            return t1.split(':', 1)[1].strip()

        def trim_txt(t1, trans=True):
            t1 = re.sub(r'[<>()*#◦◑32z+,\'\s]+', '', t1)  # 去掉特殊字符和空格
            t1 = self.trim_wan(t1)
            if trans:
                t1 = self.trans_char2unicode(t1)
            return t1

        def is_equal(ch1, ch2):
            return ch1 == ch2 or is_variant(ch1, ch2)

        def get_similar(t1, t2):
            n, t_len = 0, max(len(t1), len(t2))
            if -4 < len(t1) - len(t2) < 4:
                for i in range(t_len):
                    if i < len(t1) and i < len(t2):
                        if is_equal(t1[i], t2[i]):
                            n += 1
                        elif i + 1 < len(t1) and is_equal(t1[i + 1], t2[i]):
                            t2 = t2[:i] + '■' + t2[i:]
                        elif i + 1 < len(t2) and is_equal(t1[i], t2[i + 1]):
                            t1 = t1[:i] + '■' + t1[i:]
            return n / t_len

        def is_similar(t1, t2, strict=True, gap=2):
            g = -gap <= len(t1) - len(t2) <= gap
            if not g:
                return False
            si = get_similar(t1, t2)
            length = max(len(t1), len(t2))
            if not strict:
                if si >= 0.6 or (length <= 4 and si >= 0.5):
                    return True
            else:
                if si >= 0.75 or (length <= 4 and si >= 0.65):
                    return True

        def write_file(root1, fn1, lines1):
            not path.exists(root1) and os.makedirs(root1)
            with open(path.join(root1, fn1), 'w') as wf:
                lines1 and wf.writelines(lines1)

        def get_fin_names():
            finished_names = []
            if not names:
                files1 = glob(path.join(self.DATA_DIR, 'Text2PageF', '**', '*.txt'))
                finished_names = [fn1.rsplit('/', 1)[1].strip('.txt') for fn1 in files1]
            return finished_names

        def display_two_lines(lines1, lines2):
            size = max(len(lines1), len(lines2))
            for i in range(size):
                msg = ''
                if i < len(lines1):
                    msg += '[1]' + lines1[i].rstrip('\n')
                if i < len(lines2):
                    msg += '\t[2]' + lines2[i].rstrip('\n')
                print(msg)

        e2_names = []
        self.load_qzw()
        self.load_char2unicode()
        fin_names = get_fin_names()
        src_path = path.join(self.DATA_DIR, 'Text2Page0')
        for root, dirs, files in os.walk(src_path):
            root0 = root.replace('Text2Page0', 'Text2Page')
            for fn in files:
                name, ext = fn.rsplit('.', 1)
                if ext != 'txt' or name in fin_names or (names and name not in names):
                    continue
                # print(fn)
                lines_t = self.get_lines(fn, 'Text2Page0') or []
                lines_t = [trim_txt(ln, True) for ln in lines_t]
                lines_t = [ln for ln in lines_t if get_txt(ln)]  # 去掉空行
                txts_t = [get_txt(ln) for ln in lines_t]
                if not lines_t:
                    print('[e1]%s' % fn)
                    continue
                lines_d = self.get_lines(fn, 'DocxStdTxt') or []
                lines_d = [trim_txt(ln, False) for ln in lines_d]
                txts_d = [get_txt(ln) for ln in lines_d]  # 去掉空行
                if not lines_d:
                    print('[e2]%s' % fn)
                    continue

                # 行数相同且字数相同，则直接写入
                if len(lines_d) == len(lines_t):
                    if sum([len(ln) for ln in lines_t]) == sum([len(ln) for ln in lines_d]):
                        write_file(root0, fn, ['%02d:%s\n' % (i + 1, ln) for i, ln in enumerate(txts_d)])
                        continue

                lines, lno = [], 0
                # 从DocxStdTxt补入前面行
                if not is_similar(txts_t[0], txts_d[0]):
                    if is_similar(txts_t[0], txts_d[1], False):  # 补入前1行
                        lines.append('%02d:%s\n' % (lno + 1, txts_d[lno]))
                        lno += 1
                    elif is_similar(lines_t[0], lines_d[1], False):  # 补入前1行
                        lines.append('%02d:%s\n' % (lno + 1, txts_d[lno]))
                        lno += 1
                    elif is_similar(txts_t[0], txts_d[2]):  # 补入前2行
                        lines.append('%02d:%s\n' % (lno + 1, txts_d[lno]))
                        lines.append('%02d:%s\n' % (lno + 2, txts_d[lno + 1]))
                        lno += 2

                # 检查txts_t，逐行加入lines
                for n, txt_t in enumerate(txts_t):
                    if not txt_t:
                        continue
                    txt_tn = get_list(txts_t, n + 1)  # txts_t下1行
                    txt_t2 = txt_t + txt_tn  # txts_t当前2行
                    txt_d = get_list(txts_d, lno)  # txts_d当前行
                    txt_dn = get_list(txts_d, lno + 1)  # txts_d下1行
                    txt_d2 = txt_d + txt_dn  # txts_d当前2行

                    if is_similar(txt_t, txt_d, True, 0):  # 当前行：严格相同、字数相同，直接加入
                        lines.append('%02d:%s\n' % (lno + 1, txt_t))
                        lno += 1
                    elif is_similar(txt_t2, txt_d2, True, 0):  # 当前2行：严格相同、字数相同，进行重构
                        lines.append('%02d:%s\n' % (lno + 1, txt_t2[:len(txt_d)]))
                        set_list(txts_t, n + 1, txt_t2[len(txt_d):])
                        lno += 1
                    elif txt_d and txt_d[-1] in self.qzw and is_similar(txt_t, txt_d[:-1], True, 0):  # 当前行：差1字，补入千字文
                        lines.append('%02d:%s\n' % (lno + 1, txt_t + txt_d[-1]))
                        lno += 1
                    elif is_similar(txt_t, txt_d, True, 1):  # 当前行：严格相同，差1字，直接加入
                        lines.append('%02d:%s\n' % (lno + 1, txt_t))
                        lno += 1
                    elif is_similar(txt_t, txt_dn, False):  # 当前行：与DocxStdTxt下1行相似，先补入，再加入
                        lines.append('%02d:%s\n' % (lno + 1, txt_d))
                        lines.append('%02d:%s\n' % (lno + 2, txt_t))
                        lno += 2
                    elif is_similar(txt_t2, txt_d2, True, 1):  # 当前2行：严格相同、相差1字，进行重构
                        lines.append('%02d:%s\n' % (lno + 1, txt_t2[:len(txt_d)]))
                        set_list(txts_t, n + 1, txt_t2[len(txt_d):])
                        lno += 1
                    elif is_similar(txt_t, txt_d2, True, 1):  # 当前行：与DocxStdTxt当前2行相似，拆分当前行
                        lines.append('%02d:%s\n' % (lno + 1, txt_t[:len(txt_d)]))
                        lines.append('%02d:%s\n' % (lno + 2, txt_t[len(txt_d):]))
                        lno += 2
                    elif is_similar(txt_t2, txt_d, True, 1):  # 当前2行：与DocxStdTxt当前1行相似，合并当前2行
                        lines.append('%02d:%s\n' % (lno + 1, txt_t2))
                        set_list(txts_t, n + 1, '')
                        lno += 1
                    else:  # 剩余情况，直接加入
                        print('[e3]%s#%s, not sure: %s != %s' % (fn, lno + 1, txt_d, txt_t))
                        lines.append('%02d:%s\n' % (lno + 1, txt_t))
                        lno += 1

                # 从DocxStdTxt补入末尾行
                if len(lines_d) - len(lines) == 1 and is_similar(txts_d[lno - 1], get_txt(lines[-1])):
                    lines.append('%02d:%s\n' % (lno + 1, txts_d[lno]))
                    lno += 1
                if len(lines_d) - len(lines) == 2 and is_similar(txts_d[lno - 1], get_txt(lines[-1])):
                    lines.append('%02d:%s\n' % (lno + 1, txts_d[lno]))
                    lines.append('%02d:%s\n' % (lno + 2, txts_d[lno + 1]))
                    lno += 2

                if len(lines_d) == len(lines):
                    write_file(root0, fn, lines)
                    continue

                print('[e4]%s, line count: %s Docx != Text %s' % (fn, len(lines_d), len(lines)))
                display and display_two_lines(lines_d, lines)
                e2_names.append(fn.strip('.txt'))
                if not err_cnt:
                    print(e2_names)
                    return
                err_cnt -= 1

    def patch_note_label_to_text2page(self, names=None):
        """ 将text2page0中的夹注小字符号回写至text2page"""
        self.load_char2unicode()
        src_path = path.join(self.DATA_DIR, 'Text2Page')
        for root1, dirs, files in os.walk(src_path):
            print(root1)
            for fn in files:
                name, ext = fn.rsplit('.', 1)
                if ext != 'txt' or (names and name not in names):
                    continue
                txt = ''.join(self.get_lines(name, 'Text2Page'))
                txt = re.sub(r'\s+', '', txt)  # 去掉换行，以便比对
                txt0 = ''.join(self.get_lines(name, 'Text2Page0'))
                txt0 = re.sub(r'\s+', '', txt0)  # 去掉换行，以便比对
                txt0 = self.trans_char2unicode(txt0)
                seqs = CSequenceMatcher(None, txt, txt0, autojunk=False)
                txtn = ''
                for tag, i1, i2, j1, j2 in seqs.get_opcodes():
                    t1, t2 = txt[i1:i2], txt0[j1:j2]
                    if t2 in '<>' and not t1:
                        txtn += t2
                    else:
                        txtn += t1
                _txt = txtn.replace('<', '').replace('>', '')
                if txt != _txt:
                    print('[e1]%s, merge error:  %s[before] != %s[after]' % (name, len(txt), len(_txt)))
                else:
                    txtn = re.sub(r'(\d\d:)', r'\n\1', txtn)
                    self.write_lines(name, [ln + '\n' for ln in txtn.split('\n')], 'Text2Page')

    def stdtxt_vs_text2page(self, names=None, ignore_qzw=False):
        """ 比较两份文本"""
        logs = []
        self.load_qzw()
        src_path = path.join(self.DATA_DIR, 'DocxStdTxt')
        for root, dirs, files in os.walk(src_path):
            for fn in files:
                name, ext = fn.rsplit('.', 1)
                if ext != 'txt' or (names and name not in names):
                    continue
                root2 = root.replace('DocxStdTxt', 'Text2Page')
                if not path.exists(path.join(root2, fn)):
                    print('[e1]%s: not exist' % fn)
                    continue
                with open(path.join(root, fn), 'r') as rf:
                    lines = rf.readlines()
                with open(path.join(root2, fn), 'r') as rf2:
                    lines2 = rf2.readlines()
                if len(lines) != len(lines2):
                    print('[e2]%s lines: Docx %s != Text %s' % (fn, len(lines), len(lines2)))
                    continue
                for n, ln in enumerate(lines):
                    ln = re.sub(r'\s', '', ln)
                    ln2 = re.sub(r'[<>\s]', '', lines2[n])
                    ds = len(ln) - len(ln2)
                    if ds == 0:
                        continue
                    if ds == -1 and ln2[-1] in self.qzw:
                        if not ignore_qzw:
                            print('[e3]%s: %s != %s' % (fn, ln, ln2))
                            logs.append('[e3]%s: %s != %s\n' % (fn, ln, ln2))
                        continue
                    if ds == 1 and ln[-1] in self.qzw:
                        if not ignore_qzw:
                            print('[e4]%s: %s != %s' % (fn, ln, ln2))
                        continue
                    # print error
                    ln += '|' + (n < len(lines) - 1 and lines[n + 1].strip() or '$')
                    ln2 += '|' + (n < len(lines2) - 1 and lines2[n + 1].strip() or '$')
                    errno = 5 if len(ln) > len(ln2) else 6
                    print('[e%s]%s: %s != %s' % (errno, fn, ln, ln2))
                    break
        with open('vs_e3.log', 'w') as wf:
            wf.writelines(logs)

    def patch_qzw_2_oritxt0(self):
        if not path.exists('vs_e3.log'):
            return
        self.load_qzw()
        with open('vs_e3.log', 'r') as rf:
            for line in rf.readlines():
                mt = re.match(r'^.*(GL_\d+_\d+_\d+).txt:\s(\d\d):(.*)\s!=\s(\d\d):(.*)$', line.strip())
                if not mt:
                    continue
                name, lno1, ln1, lno2, ln2 = mt.groups()
                if lno1 == '01' and len(ln2) - len(ln1) == 1 and ln2[-1] in self.qzw:
                    print(name, ln1, ln2)
                    lines = self.get_lines(name, 'DocxOriTxt0')
                    lines[0] = lines[0].strip('\n') + ln2[-1] + '\n'
                    self.write_lines(name, lines, 'DocxOriTxt0')


def main():
    g_names = []
    gt = GlTool()

    # gt.proc_oritxt0_to_oritxt(g_names)
    # gt.proc_oritxt_to_stdtxt(g_names)
    # gt.proc_text2page0_to_text2page(g_names, 1, 500)
    # gt.stdtxt_vs_text2page(g_names, False)
    # gt.patch_note_label_to_text2page(g_names)

    # gt.print_files(g_names, 'DocxStdTxt')
    # gt.cmp_file('%s.txt' % g_names[0], 'DocxStdTxt', '', 'Text2Page0')

    # gt.find_txt('01:', 'Text', 'utf-16', 1, False)
    # gt.find_txt('<', 'Text2Page0', 'utf-8', 5)

    print('finished.')


if __name__ == '__main__':
    # case1()
    main()
