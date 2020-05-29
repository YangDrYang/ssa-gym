from astropy.coordinates import SkyCoord, ITRS, EarthLocation, AltAz
from astropy import units as u
import numpy as np
from datetime import datetime, timedelta
import time

from numpy.core._multiarray_umath import ndarray
from scipy.spatial import distance
from scipy.linalg import det

print("Running Test Cases...")

# !------------ Test 1 - GCRS to ITRS
from envs.transformations import gcrs2irts_matrix_a, get_eops, gcrs2irts_matrix_b
eop = get_eops()

xyz1: ndarray = np.array([1285410, -4797210, 3994830], dtype=np.float64)

t=datetime(year = 2007, month = 4, day = 5, hour = 12, minute = 0, second = 0)
object = SkyCoord(x=xyz1[0] * u.m, y=xyz1[1] * u.m, z=xyz1[2] * u.m, frame='gcrs',
               representation_type='cartesian', obstime=t)# just for astropy
itrs = object.transform_to(ITRS)

test1a_error = distance.euclidean(itrs.cartesian.xyz._to_value(u.m),
                                 gcrs2irts_matrix_a(t, eop) @ xyz1)
test1b_error = distance.euclidean(itrs.cartesian.xyz._to_value(u.m),
                                  gcrs2irts_matrix_b(t, eop) @ xyz1)
assert test1a_error < 25, print("Failed Test 1: GCRS to ITRS transformation")
print("Test 1a: GCRS to ITRS (a) error in meters: ", test1a_error)
print("Test 1b: GCRS to ITRS (b) error in kilometers: ", test1b_error)

# !------------ Test 2a - ITRS to LLA
from envs.transformations import itrs2lla
xyz1 = np.array(itrs.cartesian.xyz._to_value(u.m), dtype=np.float64)
lla = EarthLocation.from_geocentric(x=xyz1[0]*u.m, y=xyz1[1]*u.m, z=xyz1[2]*u.m)
lat = lla.lat.to_value(u.rad)
lon = lla.lon.to_value(u.rad)
height = lla.height.to_value(u.m)
lla = [lon, lat, height]
test2_error = lla - np.asarray(itrs2lla(xyz1))
assert np.max(test2_error) < 0.0000001, print("Failed Test 2a: ITRS to LLA transformation")
print("Test 2a: ITRS to LLA error in rads,rads,meters: ", test2_error)

# !------------ Test 2b - ITRS to LLA
from envs.transformations import itrs2lla_py
xyz1 = np.array(itrs.cartesian.xyz._to_value(u.m), dtype=np.float64)
lla = EarthLocation.from_geocentric(x=xyz1[0]*u.m, y=xyz1[1]*u.m, z=xyz1[2]*u.m)
lat = lla.lat.to_value(u.rad)
lon = lla.lon.to_value(u.rad)
height = lla.height.to_value(u.m)
lla = [lon, lat, height]
test2_error = lla - np.asarray(itrs2lla_py(xyz1))
assert np.max(test2_error) < 0.0000001, print("Failed Test 2b: ITRS to LLA transformation")
print("Test 2b: ITRS to LLA (python) error in rads,rads,meters: ", test2_error)

# !------------ Test 3 - ITRS-ITRS to AzElSr
from envs.transformations import itrs2azel
xyz1 = np.array([1285410, -4797210, 3994830], dtype=np.float64)
xyz2 = np.array([1202990, -4824940, 3999870], dtype=np.float64)

observer = EarthLocation.from_geocentric(x=xyz1[0]*u.m,y=xyz1[1]*u.m, z=xyz1[2]*u.m)
target = SkyCoord(x=xyz2[0] * u.m, y=xyz2[1] * u.m, z=xyz2[2] * u.m, frame='itrs',
               representation_type='cartesian', obstime=t)# just for astropy
AltAz_frame = AltAz(obstime=t, location=observer)
results = target.transform_to(AltAz_frame)

az1 = results.az.to_value(u.rad)
alt1 = results.alt.to_value(u.rad)
sr1 = results.distance.to_value(u.m)

aer = itrs2azel(xyz1,np.reshape(xyz2,(1,3)))[0]

test3_error = [az1-aer[0],alt1-aer[1],sr1-aer[2]]

assert np.absolute(az1 - aer[0]) < 0.001, print("Failed Test 3a: ITRS-ITRS to Az transformation")
assert np.absolute(alt1 - aer[1]) < 0.001, print("Failed Test 3b: ITRS-ITRS to El transformation")
assert np.absolute(sr1 - aer[2]) < 0.001, print("Failed Test 3c: ITRS-ITRS to Srange transformation")
print("Test 3: ITRS-ITRS to Az, El, Srange error in rads,rads,meters: ", test2_error)

# !------------ Test 4 - ITRS-ITRS to AzElSr
t=datetime(year=2007, month=4, day=5, hour=12, minute=0, second=0)
t = [t]

start = time.time()
for i in range(2880):
    t.append(t[-1]+timedelta(seconds=30))
gcrs2irts_matrix_a(t, eop)
end = time.time()
print("Test 4a: Time to generate cel2ter transformation matrix with gcrs2irts_matrix_a for every 30 seconds for an entire day: ", end-start, " seconds")

start = time.time()
for i in range(2880):
    t.append(t[-1]+timedelta(seconds=30))
gcrs2irts_matrix_b(t, eop)
end = time.time()
print("Test 4b: Time to generate cel2ter transformation matrix with gcrs2irts_matrix_b for every 30 seconds for an entire day: ", end-start, " seconds")

# !------------ Test 5 - ITRS to GCRS SOFA cases
from envs.transformations import gcrs2irts_matrix_a, gcrs2irts_matrix_b

t = datetime(year=2007, month=4, day=5, hour=12, minute=0, second=0)

Cel2Ter94 = np.asarray([[+0.973104317712772, +0.230363826174782, -0.000703163477127],
                        [-0.230363800391868, +0.973104570648022, +0.000118545116892],
                        [+0.000711560100206, +0.000046626645796, +0.999999745754058]])

Cel2Ter00aCIO = np.asarray([[+0.973104317697512, +0.230363826239227, -0.000703163482268],
                           [-0.230363800456136, +0.973104570632777, +0.000118545366806],
                           [+0.000711560162777, +0.000046626403835, +0.999999745754024]])

Cel2Ter00aEB = np.asarray([[+0.973104317697618, +0.230363826238780, -0.000703163482352],
                           [-0.230363800455689, +0.973104570632883, +0.000118545366826],
                           [+0.000711560162864, +0.000046626403835, +0.999999745754024]])

Cel2Ter06aCA = np.asarray([[+0.973104317697535, +0.230363826239128, -0.000703163482198],
                           [-0.230363800456037, +0.973104570632801, +0.000118545366625],
                           [+0.000711560162668, +0.000046626403995, +0.999999745754024]])

Cel2Ter06aXY = np.asarray([[+0.973104317697536, +0.230363826239128, -0.000703163481769],
                           [-0.230363800456036, +0.973104570632801, +0.000118545368117],
                           [+0.000711560162594, +0.000046626402444, +0.999999745754024]])

print("Test 5a: Cel2Ter06aXY vs Cel2Ter94, magnitude of error: ", det(Cel2Ter06aXY - Cel2Ter94))
print("Test 5b: Cel2Ter06aXY vs Cel2Ter00aCIO, magnitude of error: ", det(Cel2Ter06aXY - Cel2Ter00aCIO))
print("Test 5c: Cel2Ter06aXY vs Cel2Ter00aEB, magnitude of error: ", det(Cel2Ter06aXY - Cel2Ter00aEB))
print("Test 5d: Cel2Ter06aXY vs Cel2Ter06aCA, magnitude of error: ", det(Cel2Ter06aXY - Cel2Ter06aCA))
print("Test 5e: Cel2Ter06aXY vs gcrs2irts_matrix, magnitude of error: ", det(Cel2Ter06aXY - gcrs2irts_matrix_a(t, eop)))
print("Test 5f: Cel2Ter06aXY vs utc2cel06acio, magnitude of error: ", det(Cel2Ter06aXY - gcrs2irts_matrix_b(t, eop)))

# !------------ Test 6 - Filter Functions (core functions)
from envs.filter import compute_filter_weights, Q_discrete_white_noise, sigma_points, unscented_transform
from filterpy.common import Q_discrete_white_noise as Q_discrete_white_noise_fp
from filterpy.kalman import unscented_transform as unscented_transform_fp, MerweScaledSigmaPoints as MerweScaledSigmaPoints_fp
from filterpy.kalman.UKF import UnscentedKalmanFilter as UnscentedKalmanFilter_pf

# Configurable Settings:
dim_x = 6
dim_z = 3
dt = 30.0
qvar = 0.000001
obs_noise = np.repeat(100, 3)
x = np.array([34090.8583,  23944.7744,  6503.06682, -1.983785080, 2.15041744,  0.913881611])
P = np.eye(6) * np.array([100,  100,  100, 0.1, 0.1,  0.1])
alpha = 0.001
beta = 2.0
kappa = 3-6

# check weights
points_fp = MerweScaledSigmaPoints_fp(dim_x, alpha, beta, kappa)
Wc, Wm = compute_filter_weights(alpha, beta, kappa, dim_x)
Test6a = np.allclose(Wc, points_fp.Wc)
Test6b = np.allclose(Wm, points_fp.Wm)
assert Test6a, print("Failed Test 6a: points.Wc")
assert Test6b, print("Failed Test 6b: points.Wm")

# check noise function
noise = Q_discrete_white_noise(dim=2, dt=dt, var=0.000001**2, block_size=3, order_by_dim=False)
noise_fp = Q_discrete_white_noise_fp(dim=2, dt=dt, var=0.000001**2, block_size=3, order_by_dim=False)
Test6c = np.allclose(noise, noise_fp)
assert Test6c, print("Failed Test 6c: Q_discrete_white_noise")

# check sigma points
lambda_ = alpha**2 * (dim_x + kappa) - dim_x
points = sigma_points(x, P, lambda_, dim_x)
Test6d = np.allclose(points, points_fp.sigma_points(x, P))
assert Test6d, print("Failed Test 6d: sigma points")

if np.all((Test6a, Test6b, Test6c, Test6d)):
    print("Test 6: Successful: sigmas points, noise function, and weights")

'''
# check unscented transform
ut = unscented_transform(points, Wm, Wc, noise)
ut_fp = unscented_transform_fp(points, Wm, Wc, noise)
assert np.allclose(ut[0], ut_fp[0]), print("Failed Test 6e: mean from UT")
assert np.allclose(ut[1], ut_fp[1]), print("Failed Test 6f: covariance from UT")

This test was removed because it was found than when the UT matched the UT in the code, 
the predict function did not correctly calculate the mean. Could use some looking into. 
'''

# !------------ Test 7 - Filter Prediction
from envs.filter import predict
from poliastro.core.propagation import markley
from numba import njit
from envs.dynamics import fx_xyz_markley as fx, hx_xyz as hx

# Configurable Settings:
Q = noise
ukf = UnscentedKalmanFilter_pf(dim_x, dim_z, dt, hx, fx, points_fp)
ukf.x = np.copy(x)
ukf.P = np.copy(P)
ukf.Q = np.copy(Q)

# check filter predict
ukf.predict(dt)

x_post, P_post, sigmas_post = predict(x, P, Wm, Wc, Q, dt, lambda_, fx)
Test7a = np.prod((x_post-ukf.x)) / np.prod(x_post)
assert np.abs(Test7a) < 1.0e-10, print("Test 7a: Predicted means don't match")
Test7b = det((P_post-ukf.P))/det(P_post)
assert np.abs(Test7b) < 1.0e-10, print("Test 7b: Predicted covariances don't match")
Test7c = np.prod((sigmas_post-ukf.sigmas_f)) / np.prod(sigmas_post)
assert Test7c < 1.0e-10, print("Test 7c: Predicted sigmas points don't match")

print("Test 7: step 1 errors: x: ", Test7a, ", P: ", Test7b, ", sigmas:", Test7c)

ukf.predict(dt)

x_post2, P_post2, sigmas_post2 = predict(x_post, P_post, Wm, Wc, Q, dt, lambda_, fx)
Test7d = np.prod((x_post2-ukf.x)) / np.prod(x_post2)
assert np.abs(Test7d) < 1.0e-10, print("Test 7d: Predicted means don't match")
Test7e = det((P_post2-ukf.P))/det(P_post2)
assert np.abs(Test7e) < 1.0e-10, print("Test 7e: Predicted covariances don't match")
Test7f = np.prod((sigmas_post2-ukf.sigmas_f)) / np.prod(sigmas_post2)
assert Test7f < 1.0e-10, print("Test 7f: Predicted sigmas points don't match")

print("Test 7: step 2 errors: x: ", Test7d, ", P: ", Test7e, ", sigmas:", Test7f)

ukf.predict(dt)

x_post3, P_post3, sigmas_post3 = predict(x_post2, P_post2, Wm, Wc, Q, dt, lambda_, fx)

for i in range(47):
    ukf.predict(dt)
    x_post3, P_post3, sigmas_post3 = predict(x_post3, P_post3, Wm, Wc, Q, dt, lambda_, fx)

Test7h = np.prod((x_post3-ukf.x)) / np.prod(x_post3)
assert np.abs(Test7h) < 1.0e-10, print("Test 7h: Predicted means don't match")
Test7i = det((P_post3-ukf.P))/det(P_post3)
assert np.abs(Test7i) < 1.0e-10, print("Test 7i: Predicted covariances don't match")
Test7j = np.prod((sigmas_post3-ukf.sigmas_f)) / np.prod(sigmas_post2)
assert Test7j < 1.0e-10, print("Test 7j: Predicted sigmas points don't match")

print("Test 7: step 50 errors: x: ", Test7h, ", P: ", Test7i, ", sigmas:", Test7j)

# !------------ Test 8 - Filter Updates
from envs.filter import update

x_true = np.copy(x)

for i in range(50):
    x_true = fx(x_true, dt)

R = np.array([1.25, 1.25, 1.25])
z = x_true[:3]

x_post4, P_post4 = update(ukf.x, ukf.P, z, Wm, Wc, R, ukf.sigmas_f, hx)

ukf.update(z=z, R=R)

Test8a = np.prod((x_post4-ukf.x)) / np.prod(x_post4)

assert np.abs(Test8a) < 1.0e-10, print("Test 8a: Updated means don't match")
Test8b = det((P_post4-ukf.P))/det(P_post4)
assert np.abs(Test8b) < 1.0e-10, print("Test 8b: Updated covariances don't match")

print("Test 8: step 50, update 1 errors: x: ", Test8a, ", P: ", Test8b)

for i in range(50):
    ukf.predict(dt)
    x_post4, P_post4, sigmas_post4 = predict(x_post4, P_post4, Wm, Wc, Q, dt, lambda_, fx)

for i in range(50):
    x_true = fx(x_true, dt)

z = x_true[:3]

x_post4, P_post4 = update(x_post4, P_post4, z, Wm, Wc, R, sigmas_post4, hx)

ukf.update(z=z, R=R)

Test8c = np.prod((x_post4-ukf.x)) / np.prod(x_post4)
assert np.abs(Test8c) < 1.0e-10, print("Test 8c: Updated means don't match")
Test8d = det((P_post4-ukf.P))/det(P_post4)
assert np.abs(Test8d) < 1.0e-10, print("Test 8d: Updated covariances don't match")

print("Test 8: step 100, update 2 errors: x: ", Test8c, ", P: ", Test8d)

# !------------ Test 9 - Az El means and residuals
from numba import jit
from envs.dynamics import residual_z_aer as residual_z, mean_z_aer as mean_z

residual_az_cases = [0, 0.999, 90.0, 179.001, 180.001, 270.0, 359.99, 360]
residual_az_cases = np.radians(residual_az_cases)
residual_el_cases = [-180.00, -179.001, -90.0, -0.999, 0, 0.999, 90.0, 179.001, 180.00]
residual_el_cases = np.radians(residual_el_cases)
residual_sr_cases = [0.0001, -0.0001, 0, 1.0, -1.0, 1000.0, -1000.0, 1000.0001, -1000.0001]

from itertools import permutations
residual_az_cases2 = list(permutations(residual_az_cases, 2))
residual_el_cases2 = list(permutations(residual_el_cases, 2))
residual_sr_cases2 = list(permutations(residual_sr_cases, 2))

diffs = []
for az, el, sr in zip(residual_az_cases2, residual_el_cases2, residual_sr_cases2):
    aer0 = np.asarray([az[0], el[0], sr[0]])
    aer1 = np.asarray([az[1], el[1], sr[1]])
    diff = residual_z(aer0, aer1)
    az = np.round(az,4)
    el = np.round(el,4)
    sr = np.round(sr,4)
    # print(np.round(az[0],4), " - ", np.round(az[1],4), " = ", np.round(diff[0],4))
    # print(np.round(el[0],4), " - ", np.round(el[1],4), " = ", np.round(diff[1],4))
    # print(np.round(sr[0],4), " - ", np.round(sr[1],4), " = ", np.round(diff[2],4))
    diffs.append(diff)

diffs = np.array(diffs)
comps = np.array([[-0.01743584, -0.01743584,  0.0002    ],
                  [-1.57079633e+00, -1.57079633e+00,  1.00000000e-04],
                  [-3.12415681, -3.12415681, -0.9999    ],
                  [ 3.1415752 , -3.14159265,  1.0001    ],
                  [   1.57079633,    3.12415681, -999.9999    ],
                  [1.74532925e-04, 1.57079633e+00, 1.00000010e+03],
                  [ 0.00000000e+00,  1.74358392e-02, -1.00000000e+03],
                  [1.74358392e-02, 0.00000000e+00, 1.00000020e+03],
                  [-1.55336049e+00,  1.74358392e-02, -2.00000000e-04],
                  [-3.10672098e+00, -1.55336049e+00, -1.00000000e-04],
                  [-3.12417427, -3.10672098, -1.0001    ],
                  [ 1.58823217, -3.12415681,  0.9999    ],
                  [ 1.76103722e-02,  3.14159265e+00, -1.00000010e+03],
                  [1.74358392e-02, 1.58823217e+00, 9.99999900e+02],
                  [ 1.57079633e+00,  3.48716785e-02, -1.00000020e+03],
                  [1.55336049e+00, 1.74358392e-02, 1.00000000e+03],
                  [-1.55336049e+00,  1.57079633e+00, -1.00000000e-04],
                  [-1.57081378e+00,  1.55336049e+00,  1.00000000e-04],
                  [-3.14159265, -1.55336049, -1.        ],
                  [ 1.57097086, -1.57079633,  1.        ],
                  [    1.57079633,    -1.58823217, -1000.        ],
                  [   3.12415681,   -3.14159265, 1000.        ],
                  [    3.10672098,     1.58823217, -1000.0001    ],
                  [   1.55336049,    1.57079633, 1000.0001    ],
                  [-0.01745329,  3.12415681,  0.9999    ],
                  [-1.58823217,  3.10672098,  1.0001    ],
                  [3.12433135, 1.55336049, 1.        ],
                  [ 3.12415681, -0.01743584,  2.        ],
                  [-3.14157520e+00, -3.48716785e-02, -9.99000000e+02],
                  [   3.12417427,   -1.58823217, 1001.        ],
                  [   1.57081378,    3.14159265, -999.0001    ],
                  [1.74532925e-02, 3.12415681e+00, 1.00100010e+03],
                  [-1.57077887, -3.14159265, -1.0001    ],
                  [-3.14140067,  3.12415681, -0.9999    ],
                  [-3.1415752 ,  1.57079633, -1.        ],
                  [-1.57079633,  0.01743584, -2.        ],
                  [-1.58823217e+00, -1.74358392e-02, -1.00100000e+03],
                  [ -3.14159265,  -1.57079633, 999.        ],
                  [    1.58823217,    -3.12415681, -1001.0001    ],
                  [  1.57077887,  -3.14159265, 999.0001    ],
                  [ -1.57062179,  -3.12415681, 999.9999    ],
                  [  -1.57079633,   -3.14159265, 1000.0001    ],
                  [-1.74532925e-04,  1.58823217e+00,  1.00000000e+03],
                  [-1.76103722e-02,  3.48716785e-02,  9.99000000e+02],
                  [-1.57097086e+00,  1.74358392e-02,  1.00100000e+03],
                  [-3.12433135e+00, -1.55336049e+00,  2.00000000e+03],
                  [ 3.14140067e+00, -3.10672098e+00, -1.00000000e-04],
                  [ 1.57062179e+00, -3.12415681e+00,  2.00000010e+03],
                  [-1.74532925e-04, -1.57079633e+00, -1.00000010e+03],
                  [   0.        ,   -1.58823217, -999.9999    ],
                  [-1.74358392e-02, -3.14159265e+00, -1.00000000e+03],
                  [   -1.57079633,     1.58823217, -1001.        ],
                  [  -3.12415681,    1.57079633, -999.        ],
                  [ 3.14157520e+00,  1.55336049e+00, -2.00000000e+03],
                  [ 1.57079633e+00, -1.55336049e+00, -2.00000010e+03],
                  [ 1.74532925e-04, -1.57079633e+00,  1.00000000e-04]])

if np.allclose(comps,diffs):
    print("Test 9a: residuals_z successful")
else:
    print("Test 9a: residuals_z failed")

sigmas_h = np.array([[ 1.16194446e+00, -2.89490749e-01,  4.27983498e+04],
                     [ 1.16194470e+00, -2.89490524e-01,  4.27983610e+04],
                     [ 1.16194429e+00, -2.89490941e-01,  4.27983641e+04],
                     [ 1.16194415e+00, -2.89490465e-01,  4.27983519e+04],
                     [ 1.16194446e+00, -2.89490748e-01,  4.27983498e+04],
                     [ 1.16194446e+00, -2.89490749e-01,  4.27983498e+04],
                     [ 1.16194446e+00, -2.89490749e-01,  4.27983498e+04],
                     [ 1.16194422e+00, -2.89490974e-01,  4.27983385e+04],
                     [ 1.16194462e+00, -2.89490557e-01,  4.27983355e+04],
                     [ 1.16194477e+00, -2.89491033e-01,  4.27983477e+04],
                     [ 1.16194446e+00, -2.89490750e-01,  4.27983497e+04],
                     [ 1.16194446e+00, -2.89490749e-01,  4.27983498e+04],
                     [ 1.16194446e+00, -2.89490749e-01,  4.27983498e+04]])
c = np.array([1.16194447e+00, -2.89490743e-01, 4.27983502e+04])

mean_comp = np.array([ 1.16152779e+00, -2.89490749e-01,  4.27900165e+04])

mean1 = mean_z(sigmas_h, Wm)

if np.allclose(mean_comp,mean1):
    print("Test 9b: mean_z test 1 successful")
else:
    print("Test 9b: mean_z test 1 failed")

sigmas_h = np.array([[ np.pi*1e-05, np.pi - np.pi*1e-05,  40000],
                     [ np.pi*1e-01, np.pi - np.pi*1e-01,  20000],
                     [ np.pi*2 - np.pi*1e-01, -np.pi + np.pi*1e-05,  80000],
                     [ np.pi*2 - np.pi*1e-05, -np.pi + np.pi*1e-01,  60000.0],
                     [ np.pi*1e-05, np.pi - np.pi*1e-01,  50000.0]])

mean2 = mean_z(sigmas_h, np.repeat(1, 5))

mean_comp = np.array([6.40864997e-06, 3.07800526e+00, 5.00000000e+04])

if np.allclose(mean_comp,mean2):
    print("Test 9b: mean_z test 2 successful")
else:
    print("Test 9b: mean_z test 2 failed")

# !------------ Test 10 - Az El Measurement Function
from envs.transformations import lla2itrs
from envs.dynamics import hx_aer_erfa as hx, hx_aer_astropy as hx2

observer_lat = np.radians(38.828198)
observer_lon = np.radians(-77.305352)
observer_alt = np.float64(20.0) # in meters
observer_lla = np.array((observer_lon, observer_lat, observer_alt))
observer_itrs = lla2itrs(observer_lla)/1000 # meter -> kilometers

t=datetime(year = 2007, month = 4, day = 5, hour = 12, minute = 0, second = 0)

trans_matrix = gcrs2irts_matrix_a(t, eop)

hx_args1 = (trans_matrix, observer_itrs)
hx_args2 = (t, observer_lat, observer_lon, observer_alt)

z1 = hx(x, hx_args1)

z2 = hx2(x, hx_args2)

hx_error = z2 - z1

print("Test 10a: hx error in azimuth (arc seconds) = ", np.degrees(hx_error[0])*60*60)
print("Test 10b: hx error in elevation (arc seconds) = ", np.degrees(hx_error[1])*60*60)
print("Test 10c: hx error in slant range (meters) = ", np.degrees(hx_error[2])*1000)
print("I am unsure if these errors are mine or AstroPy's given the above matched. Each sub-function \n"
      "checks out against AstroPy, but the end to end case has significantly more error... \n"
      "Issue opened with AstroPy at https://github.com/astropy/astropy/issues/10407")

# !------------ Test 11 - Az El Updates
from envs.filter import compute_filter_weights, Q_discrete_white_noise, sigma_points, update, predict
from filterpy.kalman import MerweScaledSigmaPoints as MerweScaledSigmaPoints_fp
from filterpy.kalman.UKF import UnscentedKalmanFilter as UnscentedKalmanFilter_pf
from envs.dynamics import residual_xyz as residual_x, residual_z_aer as residual_z, mean_z_aer as mean_z
from envs.dynamics import fx_xyz_markley as fx, hx_aer_erfa as hx, hx_aer_kwargs as hx_dict
from envs.transformations import lla2itrs, gcrs2irts_matrix_b as gcrs2irts_matrix, get_eops
from datetime import datetime, timedelta
import numpy as np
from scipy.spatial import distance

# Sim Configurable Setting:
max_step = 500
obs_interval = 10
observer = (38.828198, -77.305352, 20.0) # lat (deg), lon (deg), height (meters)
x_init = (34090.8583,  23944.7744,  6503.06682, -1.983785080, 2.15041744,  0.913881611) # 3 x km, 3 x km/s
t_init = datetime(year=2007, month=4, day=5, hour=12, minute=0, second=0)
eop = get_eops()

# Filter Configurable Settings:
dim_x = 6
dim_z = 3
dt = 30.0
R = np.diag([np.pi/360/60/60, np.pi/360/60/60, 0.1])
Q = Q_discrete_white_noise(dim=2, dt=dt, var=0.0001**2, block_size=3, order_by_dim=False)
x = np.array([34090.8583,  23944.7744,  6503.06682, -1.983785080, 2.15041744,  0.913881611])
P = np.diag([100,  100,  100, 0.1, 0.1,  0.1])
alpha = 0.001
beta = 2.0
kappa = 3-6

# Derived Settings:
lambda_ = alpha**2 * (dim_x + kappa) - dim_x
points = sigma_points(x, P, lambda_, dim_x)
points_fp = MerweScaledSigmaPoints_fp(dim_x, alpha, beta, kappa)
Wc, Wm = compute_filter_weights(alpha, beta, kappa, dim_x)
x_true = np.copy(x)
x_filter = np.copy(x)
P_filter = np.copy(P)
t = [t_init]
step = [0]
observer_lla = np.array((np.radians(observer[1]), np.radians(observer[0]), observer[2]))
observer_itrs = lla2itrs(observer_lla)/1000 # meter -> kilometers

# FilterPy Configurable Settings:
ukf = UnscentedKalmanFilter_pf(dim_x, dim_z, dt, hx_dict, fx, points_fp)
ukf.x = np.copy(x)
ukf.P = np.copy(P)
ukf.Q = np.copy(Q)
ukf.R = np.copy(R)
ukf.residual_z = residual_z
ukf.z_mean = mean_z

# run the filter
for i in range(max_step):
    # step truth forward
    step.append(step[-1] + 1)
    t.append(t[-1] + timedelta(seconds=dt))
    x_true = fx(x_true, dt)
    # step FilterPy forward
    ukf.predict(dt)
    # step filter forward
    x_filter, P_filter, sigmas_f_filter = predict(x_filter, P_filter, Wm, Wc, Q, dt, lambda_, fx)
    # Check if obs should be taken
    if step[-1] % obs_interval == 0:
        # get obs:
        trans_matrix = gcrs2irts_matrix(t[-1], eop)
        hx_args = (trans_matrix, observer_itrs)
        hx_kwargs = {"trans_matrix": trans_matrix, "observer_itrs": observer_itrs}
        z_true = hx(x_true, hx_args)
        # update FilterPy
        ukf.update(z_true, **hx_kwargs)
        x_filter, P_filter = update(x_filter, P_filter, z_true, Wm, Wc, R, sigmas_f_filter, hx, residual_x, mean_z, residual_z, hx_args)

test11a_error = [distance.euclidean(ukf.x[:3],x_true[:3]), distance.euclidean(ukf.x[3:],x_true[3:])]
test11b_error = [distance.euclidean(x_filter[:3],x_true[:3]), distance.euclidean(x_filter[3:],x_true[3:])]

print("Test 11a: step ", max_step, " error after ", int(max_step/obs_interval), " updates (FilterPy): ",
      np.round(test11a_error[0]*1000,4), " meters, ", np.round(test11a_error[1]*1000,4), " meters per second")

print("Test 11b: step ", max_step, " error after ", int(max_step/obs_interval), " updates (Filter): ",
      np.round(test11b_error[0]*1000,4), " meters, ", np.round(test11b_error[1]*1000,4), " meters per second")

def time_filter_predict():
    global x_filter, P_filter, Wm, Wc, Q, dt, lambda_, fx
    x_filter, P_filter, sigmas_f_filter = predict(x_filter, P_filter, Wm, Wc, Q, dt, lambda_, fx)

def time_filterpy_predict():
    global ukf
    ukf.predict()

import timeit

print("Test 11c: Time to complete 500 steps using njit prediction: ", np.round(timeit.timeit(time_filter_predict, number=500),4), " seconds")
print("Test 11d: Time to complete 500 steps using FilterPy prediction: ", np.round(timeit.timeit(time_filterpy_predict, number=500),4), " seconds")

# !------------ Test 12 - Az El Updates with Uncertainty
# Sim Configurable Setting:
max_step = 2880
obs_interval = 50
observer = (38.828198, -77.305352, 20.0) # lat (deg), lon (deg), height (meters)
x_init = (34090.8583,  23944.7744,  6503.06682, -1.983785080, 2.15041744,  0.913881611) # 3 x km, 3 x km/s
t_init = datetime(year=2007, month=4, day=5, hour=12, minute=0, second=0)
eop = get_eops()

# Filter Configurable Settings:
dim_x = 6
dim_z = 3
dt = 30.0
R = np.diag([np.pi/360/60/60, np.pi/360/60/60, 0.1])
Q = Q_discrete_white_noise(dim=2, dt=dt, var=0.0001**2, block_size=3, order_by_dim=False)
x = np.array([34090.8583,  23944.7744,  6503.06682, -1.983785080, 2.15041744,  0.913881611])
P = np.diag([10,  10,  10, 0.01, 0.01,  0.01])
alpha = 0.001
beta = 2.0
kappa = 3-6

# Derived Settings:
lambda_ = alpha**2 * (dim_x + kappa) - dim_x
points = sigma_points(x, P, lambda_, dim_x)
points_fp = MerweScaledSigmaPoints_fp(dim_x, alpha, beta, kappa)
Wc, Wm = compute_filter_weights(alpha, beta, kappa, dim_x)
x_true = np.copy(x)
x_filter = np.copy(x) + np.random.normal(0,np.sqrt(np.diag(P)*1000))/1000
P_filter = np.copy(P)
t = [t_init]
step = [0]
observer_lla = np.array((np.radians(observer[1]), np.radians(observer[0]), observer[2]))
observer_itrs = lla2itrs(observer_lla)/1000 # meter -> kilometers

# FilterPy Configurable Settings:
ukf = UnscentedKalmanFilter_pf(dim_x, dim_z, dt, hx_dict, fx, points_fp)
ukf.x = np.copy(x_filter)
ukf.P = np.copy(P)
ukf.Q = np.copy(Q)
ukf.R = np.copy(R)
ukf.residual_z = residual_z
ukf.z_mean = mean_z

fault = False
# run the filter
for i in range(max_step):
    # step truth forward
    step.append(step[-1] + 1)
    t.append(t[-1] + timedelta(seconds=dt))
    x_true = fx(x_true, dt)
    # step FilterPy forward
    ukf.predict(dt)
    # step filter forward
    if not fault:
        try:
            x_filter, P_filter, sigmas_f_filter = predict(x_filter, P_filter, Wm, Wc, Q, dt, lambda_, fx)
        except np.linalg.LinAlgError:
            print("Matrix is not positive definite error on step ", step[-1], " x: ", np.round(x_filter,4), ", P: ", np.round(np.diag(P_filter),4))
            fault = True
            fault_step = np.copy(step[-1])
            fault_type = "Matrix is not positive definite"
        except not np.linalg.LinAlgError:
            print("Unknown error on step ", step[-1], " x: ", np.round(x_filter,4), ", P: ", np.round(np.diag(P_filter),4))
            fault = True
            fault_step = np.copy(step[-1])
            fault_type = "Unknown Issue"
    # Check if obs should be taken
    if step[-1] % obs_interval == 0:
        # get obs:
        trans_matrix = gcrs2irts_matrix(t[-1], eop)
        hx_args = (trans_matrix, observer_itrs)
        hx_kwargs = {"trans_matrix": trans_matrix, "observer_itrs": observer_itrs}
        z_true = hx(x_true, hx_args)
        z_noise = np.random.normal(0, np.sqrt(np.diag(R)*[360*60*60, 360*60*60, 1000]))/[360*60*60, 360*60*60, 1000]
        z_filter = z_true + z_noise
        # update FilterPy
        ukf.update(z_filter, **hx_kwargs)
        if not fault:
            x_filter, P_filter = update(x_filter, P_filter, z_filter, Wm, Wc, R, sigmas_f_filter, hx, residual_x, mean_z, residual_z, hx_args)


test12a_error = [distance.euclidean(ukf.x[:3],x_true[:3]), distance.euclidean(ukf.x[3:],x_true[3:])]
test12b_error = [distance.euclidean(x_filter[:3],x_true[:3]), distance.euclidean(x_filter[3:],x_true[3:])]

print("Test 12a: step ", max_step, " error after ", int(max_step/obs_interval), " updates (FilterPy with noise): ",
      np.round(test12a_error[0]*1000,4), " meters, ", np.round(test12a_error[1]*1000,4), " meters per second")

if not fault:
    print("Test 12b: step ", max_step, " error after ", int(max_step/obs_interval), " updates (Filter with noise): ",
          np.round(test12b_error[0]*1000,4), " meters, ", np.round(test12b_error[1]*1000,4), " meters per second")
else:
    print("Test 12b: unsuccessful with a fault on step ", fault_step, " and error type: ", fault_type)
    print("Issue is in line 429 of filter.py - U = np.linalg.cholesky((lambda_ + n)*P).T")
    print("Consider https://stats.stackexchange.com/questions/6364/making-square-root-of-covariance-matrix-positive-definite-matlab/6367#6367")
    print("This gist has some comparisons: https://gist.github.com/AshHarvey/1be1db0ae95dc99fe6efed7f2831f737")

print("Done")
