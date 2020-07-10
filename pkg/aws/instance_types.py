def compu(name,core,ram):
    if name=='general':
        if core==1 and ram==0.5:
            return('t2.nano')
        elif core==1 and ram==1:
            return('t2.micro')
        elif core==1 and ram==2:
            return('t2.small')
        elif core==2 and ram==4:
            return('t2.medium')
        elif core==2 and ram==8:
            return('t2.large')
        elif core==4 and ram==16:
            return('t2.namelarge')
        elif core==8 and ram==32:
            return('t2.2namelarge')
        elif core==2 and ram==38:
            return('m5.large')
        elif core==4 and ram==16:
            return('m5.namelarge')
        elif core==8 and ram==32:
            return('m5.2namelarge')
        elif core==16 and ram==64:
            return('m5.4namelarge')
        elif core==48 and ram==192:
            return('m5.12namelarge')
        elif core==96 and ram==384:
            return('m5.24namelarge')
        elif core==2 and ram==8:
            return('m5d.large')
        elif core==4 and ram==16:
            return('m5d.namelarge')
        elif core==8 and ram==32:
            return('m5d.2namelarge')
        elif core==8 and ram==32:
            return('m5d.2namelarge')
        elif core==16 and ram==64:
            return('m5d.4namelarge')
        elif core==48 and ram==192:
            return('m5d.12namelarge')
        elif core==96 and ram==384:
            return('m5d.24namelarge')
        else:
            return("No machines found")
    elif name=='compute':
        if core==2 and ram==4:
            return('c5.large')
        elif core==4 and ram==8:
            return('c5.namelarge')
        elif core==8 and ram==16:
            return('c5.2namelarge')
        elif core==16 and ram==32:
            return('c5.4namelarge')
        elif core==72 and ram==144:
            return('c5.18namelarge')
        elif core==2 and ram==4:
            return('c5d.large')
        elif core==4 and ram==8:
            return('c5d.namelarge')
        elif core==8 and ram==32:
            return('c5d.2namelarge')
        elif core==16 and ram==64:
            return('c5d.4namelarge')
        elif core==32 and ram==72:
            return('c5d.9namelarge')
        elif core==72 and ram==144:
            return('c5d.18namelarge')
        elif core==2 and ram==3.75:
            return('c4.large')
        elif core==4 and ram==7.5:
            return('c4.namelarge')
        elif core==8 and ram==15:
            return('c4.2namelarge')
        elif core==16 and ram==30:
            return('c4.4namelarge')
        elif core==36 and ram==60:
            return('c4.8namelarge')
        else:
            return("No machines found")
