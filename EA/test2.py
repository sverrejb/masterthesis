import subprocess

def build_cmd(candidate_name, opponent_name, nr_matches):
    return ['java', '-Xmx1024m', '-jar',
            'forge-gui-desktop-1.5.61-SNAPSHOT-jar-with-dependencies.jar', 'sim',
            '-d', candidate_name, opponent_name,
            '-n', nr_matches, '-f', 'sealed']



#total_damage = 0
wins = 0
OPPONENTS = ["GB-sealed-opponent.dck", "UWg-sealed-opponent.dck", "RG-sealed-opponent.dck",
             "BGw-sealed-opponent.dck", "UR-sealed-opponent.dck", "RW-sealed-opponent.dck"]

for challenger in OPPONENTS:
    print(challenger)
    with open("results\\tournament\\" + challenger.replace(".dck", ".txt"),"w") as file:
        file.write("This was " + challenger + "playing versus:\n\n")
    for opponent in OPPONENTS:
        print(opponent)
        wins = 0
        for i in range(25):
            print(i)
            cmd = build_cmd(challenger, opponent, str(50))
            p = subprocess.Popen(cmd, cwd="C:\\Users\\Public\\IC\\forge-gui-desktop-1.5.60", stdout=subprocess.PIPE)
            for line in p.stdout:
                line = line.decode("utf-8").strip()
                #if challenger=="RG-sealed-opponent.dck":
                #    print(line)
                # if 'combat damage to Ai(2' in line:
                #     hit_event = line.split(' ')
                #     # print(hit_event) #For debugging
                #     damage_index = hit_event.index('deals') + 1
                #     damage = int(hit_event[damage_index])
                #     total_damage += damage
                if 'Match result' in line:
                    result = line.split(' ')
            wins += int(result[4])
            p.wait()

        with open("results\\tournament\\" + challenger.replace(".dck", ".txt"), "a") as file:
            file.write(opponent + ": {}\n \n".format(wins))


