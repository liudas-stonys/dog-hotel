import program_guests
import program_hosts
import entities.mongo_setup as mongo_setup
from colorama import Fore


def main():
    mongo_setup.global_init()
    print_header()

    try:
        while True:
            status = input("\nAre you a [g]uest or [h]ost? ").strip().lower()
            switch(status)()
    except KeyboardInterrupt:
        return


def switch(status):
    switcher = {
        **dict.fromkeys(["x", "bye", "exit", "exit()"], program_hosts.exit_app),
        "g": program_guests.run,
        "h": program_hosts.run,
    }
    return switcher.get(status, program_hosts.unknown_command)


def print_header():
    dog = \
"""                   .
             .11;iit1;,  .,,.
             ,LLt1111ii1ii;::;,
             :,tLCti11i1ff1:,::.
   :LCfttLti;i::1:.:iii1ff1;:;:
   1G00000t:,,,:ii111i1tLL1;:;:.
   ;1tLti;;:,,,::;;;11iifGCti;i;.
   .i1f1;;;;;;;;;;iLGfi;ifCGCtii;.
    .i1t1ii;iiiiif0@G1;;;i11t;..
      .;tftttfLG8@@0t11iiiiii;:
        .1LLLLLCGGLfftiiiii1ii;,
       :ffffttCGCLft1i;iiii1111i,                  .:11.
      .tLLLfLf:;tft1i;;;iii111111;.              .11i.
      .fCCLLL;.itfti;;;;iii1111tt111:.          :f1i.
       iCLfLf,,itfti;;;;;iii111t1;;i1ft;.      ,tt;i.
        ,iti, ,1tft1i;;;;;;ii11i;;;ii11tt1:    ,ft;i1.
               1ffftti;;;;;1i11;;iiiiii11tti.  .;fi;;;
              .ifCLff1;;;:i1i1i;:;;iiiiii1tti. .:Lt;:i.
              .;tLCCL1i;:;tLfft1;;;;;;;;;;1tfttLLfi;ii
              :;1fL111i;:1LCCCLf1;;;;;;i1;1fLLLLfttt:
           .;i;itLLtt1i;;tLt1i;;;i;;;;;;1tfLt:::,.
           .1LfLCLf1i;;;ifLtt1i;iii1111tfL1:
                ,1LLLLft1::ittft1;:,.....                   """

    print(Fore.MAGENTA + "\n**********************  DOG HOTELS  **********************")
    print(Fore.CYAN + dog)
    print(Fore.MAGENTA + "\n**********************  DOG HOTELS  **********************\n" + Fore.WHITE)
    print("Welcome to Dog Hotels! Why are you here?\n")
    print("[g] Book a room for your dog")
    print("[h] Offer a room in your hotel")


if __name__ == "__main__":
    main()
