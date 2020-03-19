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

// #define EPS 0.0001

// double cross(double x1, double y1, double x2, double y2)
// {
//     return (x1 * y2) - (x2 * y1);
// }

// int sign(double x)
// {
//     if(x < -EPS) return -1;
//     else if(fabs(x) < EPS) return 0;
//     else return 1;
// }

// // Receives n points, x and y values, and its sector, to be evaluated as
// // colliding or not. Evaluate each point individually.
// int *col_circuit_custom(float *x, float *y, int *sector, float *outter_x, float *outter_y,
//                             float *inner_x, float *inner_y, float wall, float slow_area, int n) {
//     int *ret = malloc(sizeof(float)*n);
//     for(int i = 0; i < n; i++) {
//         ret[i] = COLLISION_NONE;

//         // test collision with the outter wall
//         float outter_ax = outter_x[sector[i]];
//         float outter_ay = outter_y[sector[i]];
//         float outter_bx = outter_x[sector[i] + 1];
//         float outter_by = outter_y[sector[i] + 1];
//         int c_outter = sign(cross(outter_bx - outter_ax, outter_by - outter_ay,
//                                 x[i] - outter_ax, y[i] - outter_ay));

//         // test collision with the outter wall
//         float inner_ax = inner_x[sector[i]];
//         float inner_ay = inner_y[sector[i]];
//         float inner_bx = inner_x[sector[i] + 1];
//         float inner_by = inner_y[sector[i] + 1];
//         int c_inner = sign(cross(inner_bx - inner_ax, inner_by - inner_ay,
//                                 x[i] - inner_ax, y[i] - inner_ay));

//         // printf("%d: %d %d\n", sector[i], c_outter, c_inner);

//         if(c_outter == c_inner)
//             ret[i] = COLLISION_WALL;
//     }

//     return ret;
// }