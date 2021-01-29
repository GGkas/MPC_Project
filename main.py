import cl_serv_components as cl_serv
import BroadcastLink as Blink
import simpy

def main():
    print('Test simulation')
    env = simpy.Environment()

    link = simpy.Store(env)
    env.process(cl_serv.client_agent('CL1', env, link))
    env.process(cl_serv.server_agent('SRV', env, link))

    env.run(until=10000)

if __name__ == '__main__':
    main()