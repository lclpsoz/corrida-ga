#include <stdlib.h>
#include <stdio.h>
#include <math.h>


#define COLLISION_NONE 0
#define COLLISION_SLOW_AREA 1
#define COLLISION_WALL 2

// Compile with:
// gcc -std=c11 -Wall -Wextra -pedantic -fPIC -shared -o collisions.so collisions.c

// Receives n points, x and y values to be evaluated as
// colliding or not. Evaluate each point individually.
int *col_circuit_ellipse(float *x, float *y, float *center, float *outter,
                            float *inner, float wall, float slow_area, int n) {
    int *ret = malloc(sizeof(float)*n);
    for(int i = 0; i < n; i++) {
        ret[i] = COLLISION_NONE;
        float p[] = {x[i], y[i]};
        float d = hypot(center[0] - p[0], center[1] - p[1]);
        float theta = atan2(-(p[1] - center[1]), p[0] - center[0]);
        float r1 = outter[0] * outter[1] / sqrt(outter[0] * outter[0] * sin(theta) * sin(theta) + 
                            outter[1] * outter[1] * cos(theta) * cos(theta));
        float r2 = inner[0] * inner[1] / sqrt(inner[0] * inner[0] * sin(theta) * sin(theta) + 
                            inner[1] * inner[1] * cos(theta) * cos(theta));
        if(d >= r1 - wall || d <= r2)
            ret[i] = COLLISION_WALL;
        else if(d <= r2 + slow_area || d >= r1 - slow_area)
            ret[i] = COLLISION_SLOW_AREA;
    }

    return ret;
}