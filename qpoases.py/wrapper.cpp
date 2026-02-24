#include <iostream>
#include <chrono>
#include <pybind11/pybind11.h>
#include <pybind11/numpy.h>
#include <qpOASES.hpp>
namespace py = pybind11;
using namespace qpOASES;

typedef float f32;
typedef double f64;
typedef uint32_t u32;
typedef uint64_t u64;
using ArrayF64 = py::array_t<f64, py::array::c_style | py::array::forcecast>;

template<typename T_dst, typename T_src>
void copy_cast(T_dst* dst, T_src* src, u32 n) {
    u32 n_bar = (n>>3)<<3;
    // Unroll to suggest vectorization
    for (u32 i=0; i<n_bar; i+=8) {
        dst[i] = (T_dst) src[i];
        dst[i+1] = (T_dst) src[i+1];
        dst[i+2] = (T_dst) src[i+2];
        dst[i+3] = (T_dst) src[i+3];
        dst[i+4] = (T_dst) src[i+4];
        dst[i+5] = (T_dst) src[i+5];
        dst[i+6] = (T_dst) src[i+6];
        dst[i+7] = (T_dst) src[i+7];
    }
    if (n > n_bar) for (u32 i=n_bar; i<n; ++i) dst[i] = (T_dst) src[i];
}

class qpoases {
private:
    QProblem* prob;
    real_t* mem;
    real_t* g;
    real_t* l;
    real_t* u;
    real_t* sol;
    u32 nx;
    u32 nc;
    u32 m;
public:
    qpoases() : prob(nullptr), mem(nullptr), g(nullptr), l(nullptr), u(nullptr), sol(nullptr), nx(0), nc(0), m(0) {}
    ~qpoases() {
        delete[] mem;
        delete prob;
    }
    void init(ArrayF64 H,
        ArrayF64 G,
        ArrayF64 g,
        ArrayF64 low,
        ArrayF64 upp,
        u32 N, u32 m, bool verbose = false);
    std::tuple<py::array_t<f64>, f64, u64> mpcsolve(ArrayF64 g_new,
        ArrayF64 low_new,
        ArrayF64 upp_new);
    py::array_t<f64> get_sol();
};

void qpoases::init(ArrayF64 H,
        ArrayF64 G,
        ArrayF64 g,
        ArrayF64 low,
        ArrayF64 upp,
        u32 N, u32 m_in, bool verbose) 
{   
    auto H_info = H.request();
    auto G_info = G.request();
    nx = H_info.shape[0];
    nc = G_info.shape[0];
    m = m_in;

    f64* H_ptr = static_cast<f64*>(H_info.ptr);
    f64* G_ptr = static_cast<f64*>(G_info.ptr);
    f64* g_ptr = static_cast<f64*>(g.request().ptr);
    f64* low_ptr = static_cast<f64*>(low.request().ptr);
    f64* upp_ptr = static_cast<f64*>(upp.request().ptr);

    real_t* mem = new real_t[nx*nx + nc*nx + nx + nc + nc + nx];
    this->mem = mem;

    real_t* H_ = mem;
    mem += nx*nx;
    
    real_t* G_ = mem;
    mem += nx*nc;
    
    real_t* g_ = mem;
    this->g = g_;
    mem += nx;

    real_t* low_ = mem;
    this->l = low_;
    mem += nc;

    real_t* upp_ = mem;
    this->u = upp_;
    mem += nc;

    this->sol = mem;
    mem += nx;

    copy_cast<real_t, f64>(H_, H_ptr, nx*nx);
    copy_cast<real_t, f64>(G_, G_ptr, nc*nx);
    copy_cast<real_t, f64>(g_, g_ptr, nx);
    copy_cast<real_t, f64>(low_, low_ptr, nc);
    copy_cast<real_t, f64>(upp_, upp_ptr, nc);

    this->prob = new QProblem(nx, nc);
    Options options;
    options.setToMPC();
	if (!verbose) options.printLevel = PL_NONE;
	this->prob->setOptions(options);

	int_t nWSR = 10000; // Maximum number of iterations
	this->prob->init(H_, g_, G_, nullptr, nullptr, low_, upp_, nWSR);
}

std::tuple<py::array_t<f64>, f64, u64> qpoases::mpcsolve(ArrayF64 g_new,
        ArrayF64 low_new,
        ArrayF64 upp_new)
{   
    f64* g_new_ptr = static_cast<f64*>(g_new.request().ptr);
    f64* low_new_ptr = static_cast<f64*>(low_new.request().ptr);
    f64* upp_new_ptr = static_cast<f64*>(upp_new.request().ptr);

    copy_cast<real_t, f64>(g, g_new_ptr, nx);
    copy_cast<real_t, f64>(l, low_new_ptr, nc);
    copy_cast<real_t, f64>(u, upp_new_ptr, nc);
    
    int_t nWSR = 10000; // Maximum number of iterations
    auto start = std::chrono::high_resolution_clock::now();
	this->prob->hotstart(g, nullptr, nullptr, l, u, nWSR);
    auto end = std::chrono::high_resolution_clock::now();
    f64 solve_time_ms = std::chrono::duration<f64, std::milli>(end - start).count();

    this->prob->getPrimalSolution(sol);

    py::array_t<f64> u0(m);
    copy_cast<f64, real_t>(static_cast<f64*>(u0.request().ptr), sol, m);

    // qpoases stores in nWSR the number of active set updates, which is n_iter - 1.
    return std::make_tuple(u0, solve_time_ms, nWSR + 1);
}

py::array_t<f64> qpoases::get_sol() {
    py::array_t<f64> pysol(nx);
    copy_cast<f64, real_t>(static_cast<f64*>(pysol.request().ptr), sol, nx);
    return pysol;
}


PYBIND11_MODULE(pyqpoases, m) {
    py::class_<qpoases>(m, "qpoases")
        .def(py::init<>())
        .def(
            "init",
            &qpoases::init,
            py::arg("H"),
            py::arg("G"),
            py::arg("g"),
            py::arg("low"),
            py::arg("upp"),
            py::arg("N"),
            py::arg("m"),
            py::arg("verbose") = false)
        .def(
            "mpcsolve",
            &qpoases::mpcsolve,
            py::arg("g_new"),
            py::arg("low_new"),
            py::arg("upp_new"))
        .def(
            "get_sol",
            &qpoases::get_sol);
}
