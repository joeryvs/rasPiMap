#include<stdio.h>
#include<stdlib.h>


int main(int argc, char const *argv[])
{

    for (size_t i = CHAR_MIN; i < CHAR_MAX; i++)
    {
        printf(" %i : %c",i,i);
    }

    return 0;
}
