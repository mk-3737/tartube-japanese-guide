import sys

def extract_msgid(pot_path, output_txt_path):
    with open(pot_path, 'r', encoding='utf-8') as f_in, \
         open(output_txt_path, 'w', encoding='utf-8') as f_out:
        msgid_lines = []
        capturing = False
        for line in f_in:
            line = line.rstrip('\n')
            if line.startswith('msgid '):
                capturing = True
                msgid_lines = []
                first_line = line[6:].strip()
                if first_line.startswith('"'):
                    msgid_lines.append(eval(first_line))
            elif capturing:
                if line.startswith('"'):
                    msgid_lines.append(eval(line))
                else:
                    capturing = False
                    full_msgid = ''.join(msgid_lines)
                    if full_msgid != '':
                        f_out.write(full_msgid.replace('\n', '\\n') + '\n')
        if capturing:
            full_msgid = ''.join(msgid_lines)
            if full_msgid != '':
                f_out.write(full_msgid.replace('\n', '\\n') + '\n')

def apply_translation(pot_path, translated_txt_path, output_po_path):
    with open(translated_txt_path, 'r', encoding='utf-8') as f:
        translations = [line.rstrip('\n').replace('\\n', '\n') for line in f]

    trans_idx = 0

    with open(pot_path, 'r', encoding='utf-8') as f_in, \
         open(output_po_path, 'w', encoding='utf-8') as f_out:

        capturing_msgid = False
        msgid_lines = []

        for line in f_in:
            if line.startswith('msgid '):
                # msgid開始
                capturing_msgid = True
                msgid_lines = []
                f_out.write(line)
                first_line = line[6:].strip()
                if first_line.startswith('"'):
                    msgid_lines.append(eval(first_line))
            elif capturing_msgid and line.startswith('"'):
                # msgid複数行部分
                msgid_lines.append(eval(line.strip()))
                f_out.write(line)
            elif capturing_msgid:
                # msgid終わり、ここでmsgstrを書く
                capturing_msgid = False
                full_msgid = ''.join(msgid_lines)

                if full_msgid == '':
                    # 空msgidのときは空msgstrのみ
                    f_out.write('msgstr ""\n')
                else:
                    if trans_idx < len(translations):
                        trans_text = translations[trans_idx]
                        trans_idx += 1
                    else:
                        trans_text = ''
                    trans_lines = trans_text.split('\n')

                    if len(trans_lines) == 1:
                        # 1行翻訳なら1行でmsgstrを書く
                        f_out.write('msgstr "{}"\n'.format(trans_lines[0].replace('"', r'\"')))
                    else:
                        # 複数行翻訳ならmsgstr ""で開始し、各行を"..."で書く
                        f_out.write('msgstr ""\n')
                        for l in trans_lines:
                            f_out.write('"{}\\n"\n'.format(l.replace('"', r'\"')))
                # ここでmsgstr書いたので、元のmsgstr行は書かない（重複防止）
                # 代わりに現在の行（msgstr行）以降の行はまだ出力しない
                # なのでこの行はスキップ（行を書かない）
                # 次ループでmsgidでない他行（コメントなど）が出たら書くようにする
            else:
                # msgidでない行はそのまま書く
                f_out.write(line)

        # ファイル終端でmsgidまだあれば（まれにある）
        if capturing_msgid:
            full_msgid = ''.join(msgid_lines)
            if full_msgid == '':
                f_out.write('msgstr ""\n')
            else:
                if trans_idx < len(translations):
                    trans_text = translations[trans_idx]
                    trans_idx += 1
                else:
                    trans_text = ''
                trans_lines = trans_text.split('\n')
                if len(trans_lines) == 1:
                    f_out.write('msgstr "{}"\n'.format(trans_lines[0].replace('"', r'\"')))
                else:
                    f_out.write('msgstr ""\n')
                    for l in trans_lines:
                        f_out.write('"{}\\n"\n'.format(l.replace('"', r'\"')))

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage:")
        print("  extract [potファイルパス] [出力txtパス]")
        print("  apply [potファイルパス] [翻訳txtパス] [出力poパス]")
        sys.exit(1)

    mode = sys.argv[1]
    if mode == "extract":
        if len(sys.argv) != 4:
            print("Usage: extract [potファイル] [出力txt]")
            sys.exit(1)
        extract_msgid(sys.argv[2], sys.argv[3])
        print(f"Extracted msgid to {sys.argv[3]}")
    elif mode == "apply":
        if len(sys.argv) != 5:
            print("Usage: apply [potファイル] [翻訳txt] [出力po]")
            sys.exit(1)
        apply_translation(sys.argv[2], sys.argv[3], sys.argv[4])
        print(f"Applied translations to {sys.argv[4]}")
    else:
        print("Unknown mode:", mode)
