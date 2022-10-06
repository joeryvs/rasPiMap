#include<stdio.h>
#include<stdlib.h>


int main(int argc, char const *argv[])
{
    int min = CHAR_MIN;
    int max = CHAR_MAX;
    int bits = CHAR_BIT;
    for (int i = min; i <= max; i++)
    {
        char b = i;
        printf("%i : %c\n",b,b);
    }
    printf("%d,%d,%d",bits,min,max);
    return 0;
}
