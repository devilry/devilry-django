package "fabric"
package "git"
package "python-dev"
package "build-essential"
package "libncurses5-dev"

############################################
#
# Bashrc
#
############################################
cookbook_file "/home/vagrant/.bash_profile" do
  source "bash_profile"
  owner "vagrant"
  group "vagrant"
  mode "0644"
end
cookbook_file "/home/vagrant/.bashrc" do
  source "bashrc"
  owner "vagrant"
  group "vagrant"
  mode "0644"
end


############################################
#
# Vim
#
############################################
package "vim"
cookbook_file "/home/vagrant/.vimrc" do
  source "vimrc"
  owner "vagrant"
  group "vagrant"
  mode "0644"
end


###########################################
#
# Desktop
#
###########################################
package "xorg"
package "lightdm"
package "openbox"


# Enable autologin with the vagrant user (see /usr/share/xsessions/ for session names)
# NOTE: Does not seem to work!
cookbook_file "/etc/lightdm/lightdm.conf" do
  source "lightdm.conf"
  owner "root"
  group "root"
  mode "0644"
end

# Make xterm use pretty colors and font
cookbook_file "/home/vagrant/.Xresources" do
  source "Xresources"
  owner "vagrant"
  group "vagrant"
  mode "0644"
end
cookbook_file "/home/vagrant/.xinitrc" do
  source "xinitrc"
  owner "vagrant"
  group "vagrant"
  mode "0644"
end

# Configure openbox to autostart xterm
directory "/home/vagrant/.config/openbox" do
  owner "vagrant"
  group "vagrant"
  mode "0755"
  recursive true
  action :create
end
cookbook_file "/home/vagrant/.config/openbox/autostart" do
  source "openbox_autostart"
  owner "vagrant"
  group "vagrant"
  mode "0644"
end



#######################################
#
# Opera browser repo
#
#######################################
cookbook_file "/etc/apt/sources.list.d/opera.list" do
  source "aptrepo_opera"
  owner "root"
  group "root"
  mode "0644"
end
bash "add_opera_aptkey" do
  user "root"
  cwd "/root"
  not_if "test -f /root/operaarchive.key"
  code <<-EOH
  wget -O /root/operaarchive.key http://deb.opera.com/archive.key
  cat /root/operaarchive.key | sudo apt-key add -
  apt-get update
  EOH
end



#########################################
#
# Needed by Devilry
#
#########################################
package "python-virtualenv"
package "chromium-browser"
package "firefox"
package "opera"
