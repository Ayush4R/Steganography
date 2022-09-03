import sys
import os
import cv2

# File Objects creation
pix = cv2.imread('stego.png')
outp = open('output_message.txt', "w")
lg = open("embedlog.log", "r")

# Initialisation
curr_char_no = 1
text_chararcter = ""


def main():
    global text_chararcter, curr_char_no
    while True:

        # Read each line from log file
        curr_line_of_log = lg.readline()

        # Check if log file reached its end
        if len(curr_line_of_log) == 0:
            # Write extracted data to file
            outp.write(chr(int(text_chararcter, 2)))
            break

        # Unpack line read from log file to variables
        i, j, pixel, diff, pad, charNum = curr_line_of_log.split()

        # Process variables
        i = int(i)
        j = int(j)
        diff = int(diff)
        pad = int(pad)
        charNum = int(charNum)
        b, g, r = pix[i, j]

        # Check if a new character in embed log is reached
        if curr_char_no != charNum:
            outp.write(chr(int(text_chararcter, 2)))
            text_chararcter = ""

        # If embedded pixel is red
        if pixel == "r":
            binr = bin(r)
            text_chararcter += binr[(len(binr) - diff):]

        # If embedded pixel is green
        elif pixel == "g":
            binr = bin(g)
            text_chararcter += binr[(len(binr) - diff):]

        # If embedded pixel is blue
        elif pixel == "b":
            binr = bin(b)
            text_chararcter += binr[(len(binr) - diff):]

        # remove padding if required
        if pad != 0:
            text_chararcter = text_chararcter[: (len(text_chararcter) - pad)]

        # check if new character is reached
        curr_char_no = charNum

    # Close file objects
    outp.close()
    lg.close()
    print("Message decoded\nExiting!")


if __name__ == "__main__":
    main()