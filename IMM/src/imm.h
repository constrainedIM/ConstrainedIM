class Math{
    public:
        static double log2(int n){
            return log(n) / log(2);
        }
        static double logcnk(int n, int k) {
            double ans = 0;
            for (int i = n - k + 1; i <= n; i++)
            {
                ans += log(i);
            }
            for (int i = 1; i <= k; i++)
            {
                ans -= log(i);
            }
            return ans;
        }
};
class Imm
{
    private:
        //static InfGraph g;
        //static int k;
        //static map<string, string> arg;

        static double step1(InfGraph &g, const Argument & arg)
        {
            double epsilon_prime = arg.epsilon * sqrt(2);
            Timer t(1, "step1");
            for (int x = 1; ; x++)
            {
                int64 ci = (2+2/3 * epsilon_prime)* ( log(g.n) + Math::logcnk(g.n, arg.k) + log(Math::log2(g.n))) * pow(2.0, x) / (epsilon_prime* epsilon_prime);
                g.build_hyper_graph_r(ci, arg);
                
		double ept = g.build_seedset(arg.k);
                //double estimate_influence = ept * g.n;
                //INFO(x, estimate_influence);
                if (ept > 1 / pow(2.0, x))
                {
                    double OPT_prime = ept * g.n / (1+epsilon_prime);
                    //INFO("step1", OPT_prime);
                    //INFO("step1", OPT_prime * (1+epsilon_prime));
                    return OPT_prime;
                }
            }
            ASSERT(false);
            return -1;
        }
        static double step2(InfGraph &g, const Argument & arg, double OPT_prime)
        {
            Timer t(2, "step2");
            ASSERT(OPT_prime > 0);
            double e = exp(1);
            double alpha = sqrt(log(g.n) + log(2));
            double beta = sqrt((1-1/e) * (Math::logcnk(g.n, arg.k) + log(g.n) + log(2)));

            int64 R = 2.0 * g.n *  sqr((1-1/e) * alpha + beta) /  OPT_prime / arg.epsilon / arg.epsilon ;

            //R/=100;
            g.build_hyper_graph_r(R, arg);
            
			double opt = g.build_seedset(arg.k)*g.n;
            return opt;
        }
        static double step3(InfGraph &g, const Argument & arg)
        {
            double epsilon_prime = arg.epsilon * sqrt(2);
            Timer t(3, "step3");
            for (int x = 1; ; x++)
            {
                //int64 ci = (2+2/3 * epsilon_prime)* ( log(g.n) + Math::logcnk(g.n, arg.k) + log(Math::log2(g.n))) * pow(2.0, x) / (epsilon_prime* epsilon_prime);
		int64 ci = (2+2/3 * epsilon_prime)* ( log(g.protected_group_size) + Math::logcnk(g.protected_group_size, arg.k) + log(Math::log2(g.protected_group_size))) * pow(2.0, x) / (epsilon_prime* epsilon_prime);
                g.build_protected_hyper_graph_r(ci, arg);
                
		double ept = g.test_seedset(arg.k);
                //double estimate_influence = ept * g.protected_group_size;
                //INFO(x, estimate_influence);
                if (ept > 1 / pow(2.0, x))
                {
                    double OPT_prime = ept * g.protected_group_size / (1+epsilon_prime);
                    //INFO("step1", OPT_prime);
                    //INFO("step1", OPT_prime * (1+epsilon_prime));
                    return OPT_prime;
                }
            }
            ASSERT(false);
            return -1;
        }

    public:
        static void InfluenceMaximize(InfGraph &g, const Argument &arg)
        {
            Timer t(100, "InfluenceMaximize(Total Time)");

            INFO("########## Step1 ##########");

            // debugging mode lalala
            double OPT_prime;
            OPT_prime = step1(g, arg ); //estimate OPT



            INFO("########## Step2 ##########");


            double opt_lower_bound = OPT_prime;
            INFO(opt_lower_bound);
            step2(g, arg, OPT_prime);
            //INFO("step2 finish");
		
	if(g.protected_group_size > 0 && g.protected_group_size <= g.n){
	    INFO("########## Step3 ##########");
	    double protected_opt_lower_bound;
            protected_opt_lower_bound = step3(g, arg ); //estimate OPT
	    INFO(protected_opt_lower_bound);
	}
	else{
		INFO("protected_group_size is either 0 or larger than num of nodes, ignoring protected group");
		double protected_opt_lower_bound = 0;
		INFO(protected_opt_lower_bound);
	}
//INFO("########## Step4 ##########");
	    //double opt_lower_bound2;
            //opt_lower_bound2 = step4(g, arg ); //estimate OPT
	    //INFO(opt_lower_bound2);

        }

};

