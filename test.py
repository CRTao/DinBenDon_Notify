import pandas

t = "0\n$0\n管理…\nNellie_10/23五 發起的 春陽茶事 - 竹北博愛店»我也要訂\n* 預定於 10/22 (週四) 下午 06:00 截止\n10/23 飲料團\n10\n$815\n管理…\nSW_10/23五 發起的 Go義式義大利麵»我也要訂\n6\n$515\n管理…\nSW_10/22四 發起的 熊川屋日式咖哩»我也要訂\n"

l = ['0', '$0', 'Nellie', '春陽茶事 - 竹北博愛店', '* 預定於 10/22 (週四) 下午 06:00 截止', '10/23 飲料團', '10', '$815', 'SW_10/23五', 'Go義式義大利麵', '6', '$515', 'SW_10/22四', '熊川屋日式咖哩']

#print(t)

menu = t.replace('管理…\n','').replace('»我也要訂','').replace(' 發起的 ','\n').split('\n')

print(menu)

counter = 0
string = ""
tmp = []
final = []

for row in menu:
    if row.isnumeric():
        tmp.append(string)
        counter = 0
        string = ""
        final.append(tmp)
        tmp=[]
        tmp.append(row)
    else:
        counter = counter+1
        if counter > 3 :
            string = string + str(row) + " "
        else:
            tmp.append(row)
    print(tmp)
del final[0]

print(final)

order = pandas.DataFrame (final,columns=['People','Price','Date','Title','Note'])
order.sort_values(by=['Date'], inplace=True)
print(order.to_string(columns=['People','Price','Date','Title'],index=False))