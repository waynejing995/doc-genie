/* Sample C code for testing tree-sitter extraction */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define MAX_SIZE 100

typedef struct {
    int id;
    char name[50];
    double value;
} Item;

/* Initialize an item with given values */
Item* create_item(int id, const char* name, double value) {
    Item* item = malloc(sizeof(Item));
    if (item == NULL) {
        return NULL;
    }
    item->id = id;
    strncpy(item->name, name, sizeof(item->name) - 1);
    item->value = value;
    return item;
}

/* Free an item's memory */
void destroy_item(Item* item) {
    if (item != NULL) {
        free(item);
    }
}

/* Print item information */
void print_item(const Item* item) {
    if (item != NULL) {
        printf("Item %d: %s = %.2f\n", item->id, item->name, item->value);
    }
}

/* Calculate sum of item values */
double calculate_sum(Item* items[], int count) {
    double sum = 0.0;
    for (int i = 0; i < count; i++) {
        if (items[i] != NULL) {
            sum += items[i]->value;
        }
    }
    return sum;
}

/* Main function */
int main(int argc, char* argv[]) {
    Item* items[3];

    items[0] = create_item(1, "Alpha", 10.5);
    items[1] = create_item(2, "Beta", 20.3);
    items[2] = create_item(3, "Gamma", 30.1);

    for (int i = 0; i < 3; i++) {
        print_item(items[i]);
    }

    double total = calculate_sum(items, 3);
    printf("Total: %.2f\n", total);

    for (int i = 0; i < 3; i++) {
        destroy_item(items[i]);
    }

    return 0;
}