#include <stdlib.h>
#include <stdio.h>
#include <math.h>


#define COLLISION_NONE 0
#define COLLISION_SLOW_AREA 1
#define COLLISION_WALL 2

// Compile with:
// cd src && gcc -std=c11 -Wall -Wextra -pedantic -fPIC -shared -o collisions.so collisions.c && cd ..

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

#define EPS 0.0001

double cross(double x1, double y1, double x2, double y2)
{
    return (x1 * y2) - (x2 * y1);
}

int sign(double x)
{
    if(x < -EPS) return -1;
    else if(fabs(x) < EPS) return 0;
    else return 1;
}

// // Receives n points, x and y values, and its sector, to be evaluated as
// // colliding or not. Evaluate each point individually.
int **col_circuit_custom(float *x, float *y, int num_sectors, float *outter_x, float *outter_y,
                            float *inner_x, float *inner_y, float wall, float slow_area, int n) {
    int **ret = malloc(sizeof(int*)*2);
    ret[0] = malloc(sizeof(int)*n); // sector
    ret[1] = malloc(sizeof(int)*n); // collision

    for(int i = 0; i < n; i++)
        ret[0][i] = -1;

    for(int i = 0; i < n; i++) {
        for(int sector = 0; sector < num_sectors; sector++) {
            float outter_ax = outter_x[sector];
            float outter_ay = -outter_y[sector];
            float outter_bx = outter_x[sector + 1];
            float outter_by = -outter_y[sector + 1];

            float inner_ax = inner_x[sector];
            float inner_ay = -inner_y[sector];
            float inner_bx = inner_x[sector + 1];
            float inner_by = -inner_y[sector + 1];
            
            // test collision with the sector segment 1
            int c_sector1 = sign(cross(outter_ax - inner_ax, outter_ay - inner_ay,
                                    x[i] - inner_ax, y[i] - inner_ay));
                         
            // test collision with the sector segment 2
            int c_sector2 = sign(cross(outter_bx - inner_bx, outter_by - inner_by,
                                    x[i] - inner_bx, y[i] - inner_by));

            if(c_sector1 == c_sector2)
                continue;

            // test collision with the outter wall
            int c_outter = sign(cross(outter_bx - outter_ax, outter_by - outter_ay,
                                    x[i] - outter_ax, y[i] - outter_ay));
            // test collision with the inner wall
            int c_inner = sign(cross(inner_bx - inner_ax, inner_by - inner_ay,
                                    x[i] - inner_ax, y[i] - inner_ay));

            if(c_inner == c_outter)
                continue;

            ret[0][i] = sector;
        }
    }

    for(int i = 0; i < n; i++) {
        if(ret[0][i] == -1)
            ret[1][i] = COLLISION_WALL;
        else
            ret[1][i] = COLLISION_NONE;
    }

    return ret;
}