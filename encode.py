import sys
import os
import cv2

# Taking input from user
cover_image_path = input("Enter file path to cover image: ")
secret_text_path = input("Enter file path to secret file: ")
# cover_image_path = ("lenna.png")
# secret_text_path = ("message.txt")

input = open(secret_text_path, "r")
pix = cv2.imread(cover_image_path)

lg = open("embedlog.log", "w")

# initializing variable
no_of_rows, no_of_columns = pix.shape[0], pix.shape[1]


completed = 0
retrieved = ""
count = 0
paddbits = "0000000"

# read first line from secret file
curr_char_of_text = input.read(1)
charNum = 1
# if file is empty, exit
if len(curr_char_of_text) == 0:
    print("\nEmpty i/p File!")
    sys.exit("Exiting...")

b = ord(curr_char_of_text)
bitstring = bin(b)
bits = bitstring[2:]

capacity = 0
lix = no_of_rows // 3
liy = no_of_columns // 3

# Classify pixels based on the difference in pixel value to the number of bits to be substituted to LSB


def classify(pvd):
    nbits = 0
    if pvd <= 16:
        nbits = 1
    elif 16 < pvd < 32:
        nbits = 2
    else:
        nbits = 3
    return nbits


# Calculate embedding capacity of the given cover image
def calcCapacity():
    global capacity

    # Divide image into 3x3 matrix of pixels
    for i in range(0, lix * 3, 3):
        for j in range(0, liy * 3, 3):

            # Obtain pixel values of reference pixel
            bref, gref, rref = pix[i + 1, j + 1]

            # For all pixels in the matrix except the reference pixel
            for k in range(i, (i + 3)):
                if k >= no_of_rows:
                    break
                for l in range(j, (j + 3)):
                    if k == i + 1 and l == j + 1:
                        continue
                    if l >= no_of_columns:
                        break

                    # read current pixel values
                    b, g, r = pix[k, l]
                    # determine absolute difference
                    rdif = abs(int(r) - int(rref))
                    gdif = abs(int(g) - int(gref))
                    bdif = abs(int(b) - int(bref))

                    # calculate capacity

                    capacity += classify(rdif) + \
                        classify(gdif) + classify(bdif)

    # Return capacity
    return capacity


# Function to embed data to pixel
def embedbits(i, j, pixel, diff, colorpixel):
    global bits, count, bitstring, paddbits, curr_char_of_text, completed, retrieved, input, charNum

    # Initialise
    pad = 0
    nb = diff

    # if replacable bits in current pixel is less than required bits for current character
    if nb < len(bits):

        # Initialise
        curr_bits_to_be_stored = bits[:nb]  # bits to be added
        bits = bits[nb:]  # truncate character bits
        bival = bin(colorpixel)
        bival = bival[2:]
        newbival = bival[: (
            len(bival) - len(curr_bits_to_be_stored))] + curr_bits_to_be_stored

        # Write data to log File for extraction
        lg.write("%s %s %s %s %s %s %s" %
                 (i, j, pixel, diff, pad, charNum, "\n"))

        # Return new pixel value after embedding
        return int(newbival, 2)

    # if replacable bits in current pixel is greater than required
    # add padding to the character bits
    else:

        # add padding
        pad = nb - len(bits)
        curr_bits_to_be_stored = bits + paddbits[: pad]

        bival = bin(colorpixel)
        bival = bival[2:]
        newbival = bival[: (
            len(bival) - len(curr_bits_to_be_stored))] + curr_bits_to_be_stored
        count += 1

        # Write data to log File for extraction
        lg.write("%s %s %s %s %s %s %s" %
                 (i, j, pixel, diff, pad, charNum, "\n"))

        # Read new char. for embedding
        curr_char_of_text = input.read(1)

        # Check if secret file reached its end
        if len(curr_char_of_text) == 0:
            print("Embedding Completed")

            # Close input file object
            input.close()

            # Activate complete flag
            completed = 1

            # Return new pixel value after embedding
            return int(newbival, 2)

        b = ord(curr_char_of_text)
        bitstring = bin(b)
        bits = bitstring[2:]
        retrieved = ""

        # Increment the char count of embedded data
        charNum += 1

        # Return new pixel value after embedding
        return int(newbival, 2)


# Main Function
def main():

    # Initialise counter to count number of bits embedded
    embedded = 0

    # Print total Embedding capacity
    print("Total Embd. Capacity: ", calcCapacity())

    # check if size of secret file is greater than capacity
    if os.path.getsize(secret_text_path)*7 > capacity:
        sys.exit("Input file too large for given cover image\nExiting")

    # Divide image into 3x3 matrix of pixels
    for i in range(0, lix * 3, 3):
        for j in range(0, liy * 3, 3):

            # Obtain pixel values of reference pixel
            bref, gref, rref = pix[i + 1, j + 1]

            # For all pixels in the matrix except the reference pixel
            for k in range(i, (i + 3)):
                if k >= no_of_rows:
                    break
                for l in range(j, (j + 3)):
                    if k == i + 1 and l == j + 1:
                        continue
                    if l >= no_of_columns:
                        break

                    # read current pixel values
                    b, g, r = pix[k, l]
                    # determine absolute difference
                    rdif = abs(int(r) - int(rref))
                    gdif = abs(int(g) - int(gref))
                    bdif = abs(int(b) - int(bref))

                    # Till embedding gets completed
                    if completed == 0:
                        newr = embedbits(k, l, "r", classify(rdif), r)
                    if completed == 0:
                        newg = embedbits(k, l, "g", classify(gdif), g)
                    if completed == 0:
                        newb = embedbits(k, l, "b", classify(bdif), b)

                    # Assign modified pixel values
                    pix[k, l] = (newb, newg, newr)

                    # Calculate number of bits embedded till now
                    embedded += classify(rdif) + \
                        classify(gdif) + classify(bdif)

                    # Embedding completed
                    if completed == 1:

                        # Save stego image
                        cv2.imwrite("stego.png", pix)

                        # Close log file
                        lg.close()

                        # print total number of bits embedded
                        print("Embedded:", embedded, "bits")

                        # Exit program
                        sys.exit("Done..Exiting main prog.")

    # Exit if Data size greater than embedding capacity
    sys.exit("Data size greater than embedding capacity!\nExiting")


if __name__ == "__main__":
    main()
